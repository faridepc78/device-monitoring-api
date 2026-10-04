from .models import Alert, Telemetry

ALERT_TEMPERATURE_THRESHOLD = 70


def create_telemetry_with_alert(*, device, temperature, power, voltage, timestamp):
    telemetry = Telemetry.objects.create(
        device=device,
        temperature=temperature,
        power=power,
        voltage=voltage,
        timestamp=timestamp,
    )

    if temperature > ALERT_TEMPERATURE_THRESHOLD:
        Alert.objects.create(
            device=device,
            alert_type=Alert.AlertType.HIGH_TEMPERATURE,
            value=temperature,
        )

    return telemetry
