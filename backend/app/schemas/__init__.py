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
from app.schemas.recommendation import (
    RecommendationBase,
    RecommendationResponse,
    RecommendationActionRequest,
)
from app.schemas.action import (
    ActionBase,
    ActionResponse,
    ActionCreateRequest,
    ActionCompleteRequest,
    ActionCancelRequest,
    AlertResolveRequest,
)
from app.schemas.impact import (
    ImpactRecordBase,
    ImpactResponse,
    ImpactDetailResponse,
    ImpactSummaryResponse,
)

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
    "RecommendationBase",
    "RecommendationResponse",
    "RecommendationActionRequest",
    "ActionBase",
    "ActionResponse",
    "ActionCreateRequest",
    "ActionCompleteRequest",
    "ActionCancelRequest",
    "AlertResolveRequest",
    "ImpactRecordBase",
    "ImpactResponse",
    "ImpactDetailResponse",
    "ImpactSummaryResponse",
    "AuditEventBase",
    "AuditEventResponse",
    "EquipmentBase",
    "EquipmentListItem",
    "EquipmentDetailResponse",
    "DashboardKPIResponse",
]


