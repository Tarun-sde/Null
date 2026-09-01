from app.schemas.site import SiteBase, SiteResponse
from app.schemas.operator import OperatorBase, OperatorResponse
from app.schemas.telemetry import (
    TelemetryBase,
    TelemetryResponse,
    TelemetryIngestRequest,
    TelemetryStreamEvent,
)
from app.schemas.rental import (
    RentalBase,
    RentalResponse,
    CheckoutRequest,
    CheckoutResponse,
    CheckinRequest,
    CheckinResponse,
)
from app.schemas.alert import AlertBase, AlertResponse
from app.schemas.anomaly import AnomalyResponse, FleetAnomalySummary
from app.schemas.forecast import ForecastBase, ForecastResponse, ForecastFleetSummary
from app.schemas.audit import AuditEventBase, AuditEventResponse
from app.schemas.equipment import EquipmentBase, EquipmentListItem, EquipmentDetailResponse
from app.schemas.dashboard import DashboardKPIResponse

__all__ = [
    "SiteBase",
    "SiteResponse",
    "OperatorBase",
    "OperatorResponse",
    "TelemetryBase",
    "TelemetryResponse",
    "TelemetryIngestRequest",
    "TelemetryStreamEvent",
    "RentalBase",
    "RentalResponse",
    "CheckoutRequest",
    "CheckoutResponse",
    "CheckinRequest",
    "CheckinResponse",
    "AlertBase",
    "AlertResponse",
    "AnomalyResponse",
    "FleetAnomalySummary",
    "ForecastBase",
    "ForecastResponse",
    "ForecastFleetSummary",
    "AuditEventBase",
    "AuditEventResponse",
    "EquipmentBase",
    "EquipmentListItem",
    "EquipmentDetailResponse",
    "DashboardKPIResponse",
]

