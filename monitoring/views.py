from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Alert, Device
from .serializers import (
    AlertSerializer,
    DeviceSerializer,
    TelemetryHistoryQuerySerializer,
    TelemetrySerializer,
)


class TelemetryPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=["get"])
    def latest(self, request, pk=None):
        device = self.get_object()
        telemetry = device.telemetries.first()

        if telemetry is None:
            return Response(
                {"detail": "No telemetry found for this device."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TelemetrySerializer(telemetry)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="telemetry")
    def telemetry(self, request, pk=None):
        device = self.get_object()

        query_serializer = TelemetryHistoryQuerySerializer(
            data={
                "from_date": request.query_params.get("from"),
                "to_date": request.query_params.get("to"),
            }
        )
        query_serializer.is_valid(raise_exception=True)

        queryset = device.telemetries.all()

        from_date = query_serializer.validated_data.get("from_date")
        to_date = query_serializer.validated_data.get("to_date")

        if from_date:
            queryset = queryset.filter(timestamp__date__gte=from_date)

        if to_date:
            queryset = queryset.filter(timestamp__date__lte=to_date)

        paginator = TelemetryPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = TelemetrySerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(serializer.data)


class TelemetryCreateView(generics.CreateAPIView):
    serializer_class = TelemetrySerializer


class AlertListView(generics.ListAPIView):
    queryset = Alert.objects.select_related("device").all()
    serializer_class = AlertSerializer
