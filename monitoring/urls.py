from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlertListView, DeviceViewSet, TelemetryCreateView

router = DefaultRouter()
router.register("devices", DeviceViewSet, basename="device")


urlpatterns = [
    path("", include(router.urls)),
    path("telemetry/", TelemetryCreateView.as_view(), name="telemetry-create"),
    path("alerts/", AlertListView.as_view(), name="alert-list"),
]
