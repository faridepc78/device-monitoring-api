from rest_framework import serializers

from .models import Alert, Device, Telemetry
from .services import create_telemetry_with_alert


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "id",
            "name",
            "code",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TelemetrySerializer(serializers.ModelSerializer):
    device_code = serializers.CharField(write_only=True)
    device = serializers.CharField(source="device.code", read_only=True)

    class Meta:
        model = Telemetry
        fields = [
            "id",
            "device",
            "device_code",
            "temperature",
            "power",
            "voltage",
            "timestamp",
        ]
        read_only_fields = ["id", "device"]

    def validate_device_code(self, value):
        if not Device.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(
                "Active device with this code does not exist."
            )

        return value

    def validate(self, attrs):
        if attrs.get("power") is not None and attrs["power"] < 0:
            raise serializers.ValidationError({"power": "Power cannot be negative."})

        if attrs.get("voltage") is not None and attrs["voltage"] < 0:
            raise serializers.ValidationError(
                {"voltage": "Voltage cannot be negative."}
            )

        return attrs

    def create(self, validated_data):
        device_code = validated_data.pop("device_code")

        device = Device.objects.get(
            code=device_code,
            is_active=True,
        )

        return create_telemetry_with_alert(
            device=device,
            **validated_data,
        )


class AlertSerializer(serializers.ModelSerializer):
    device = serializers.CharField(source="device.code", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id",
            "device",
            "alert_type",
            "value",
            "created_at",
            "is_resolved",
        ]
        read_only_fields = [
            "id",
            "device",
            "alert_type",
            "value",
            "created_at",
        ]


class TelemetryHistoryQuerySerializer(serializers.Serializer):
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError('"from" must be before or equal to "to".')

        return attrs
