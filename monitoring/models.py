from django.db import models


class Device(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Telemetry(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="telemetries",
    )
    temperature = models.FloatField()
    power = models.FloatField()
    voltage = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["device", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.device.code} - {self.timestamp}"


class Alert(models.Model):
    class AlertType(models.TextChoices):
        HIGH_TEMPERATURE = "high_temperature", "High Temperature"

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    alert_type = models.CharField(
        max_length=50,
        choices=AlertType.choices,
    )
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.device.code} - {self.alert_type}"
