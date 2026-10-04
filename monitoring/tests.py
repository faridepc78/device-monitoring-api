from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Alert, Device, Telemetry


class DeviceAPITests(APITestCase):
    def test_create_device(self):
        data = {
            "name": "Inverter 001",
            "code": "INV-001",
            "is_active": True,
        }

        response = self.client.post(
            reverse("device-list"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Device.objects.first().code, "INV-001")


class TelemetryAPITests(APITestCase):
    def setUp(self):
        self.device = Device.objects.create(
            name="Inverter 001",
            code="INV-001",
            is_active=True,
        )

    def test_create_telemetry(self):
        data = {
            "device_code": "INV-001",
            "temperature": 42.5,
            "power": 1250,
            "voltage": 380,
            "timestamp": "2026-10-04T10:00:00Z",
        }

        response = self.client.post(
            reverse("telemetry-create"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Telemetry.objects.count(), 1)

    def test_latest_telemetry(self):
        Telemetry.objects.create(
            device=self.device,
            temperature=40,
            power=1000,
            voltage=380,
            timestamp="2026-10-04T09:00:00Z",
        )

        Telemetry.objects.create(
            device=self.device,
            temperature=45,
            power=1200,
            voltage=381,
            timestamp="2026-10-04T10:00:00Z",
        )

        response = self.client.get(reverse("device-latest", args=[self.device.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["temperature"], 45.0)

    def test_high_temperature_creates_alert(self):
        data = {
            "device_code": "INV-001",
            "temperature": 75,
            "power": 1300,
            "voltage": 381,
            "timestamp": "2026-10-04T10:00:00Z",
        }

        response = self.client.post(
            reverse("telemetry-create"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Alert.objects.count(), 1)

        alert = Alert.objects.first()
        self.assertEqual(alert.value, 75)
        self.assertEqual(
            alert.alert_type,
            Alert.AlertType.HIGH_TEMPERATURE,
        )

    def test_invalid_device_code(self):
        data = {
            "device_code": "UNKNOWN",
            "temperature": 40,
            "power": 1000,
            "voltage": 380,
            "timestamp": "2026-10-04T10:00:00Z",
        }

        response = self.client.post(
            reverse("telemetry-create"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Telemetry.objects.count(), 0)

    def test_negative_power_is_invalid(self):
        data = {
            "device_code": "INV-001",
            "temperature": 40,
            "power": -1,
            "voltage": 380,
            "timestamp": "2026-10-04T10:00:00Z",
        }

        response = self.client.post(
            reverse("telemetry-create"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Telemetry.objects.count(), 0)

    def test_latest_telemetry_not_found(self):
        response = self.client.get(reverse("device-latest", args=[self.device.id]))

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_telemetry_history_date_filter(self):
        Telemetry.objects.create(
            device=self.device,
            temperature=40,
            power=1000,
            voltage=380,
            timestamp="2026-10-01T10:00:00Z",
        )

        Telemetry.objects.create(
            device=self.device,
            temperature=45,
            power=1200,
            voltage=381,
            timestamp="2026-10-04T10:00:00Z",
        )

        response = self.client.get(
            reverse("device-telemetry", args=[self.device.id]),
            {
                "from": "2026-10-04",
                "to": "2026-10-04",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["temperature"],
            45.0,
        )
