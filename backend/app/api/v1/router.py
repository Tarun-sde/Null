from fastapi import APIRouter, Depends
from app.api.v1.auth import router as auth_router
from app.api.v1.equipment import router as equipment_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.rentals import router as rentals_router
from app.api.v1.sites import router as sites_router
from app.api.v1.operators import router as operators_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.anomalies import router as anomalies_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.forecasts import router as forecasts_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.actions import router as actions_router
from app.api.v1.impact import router as impact_router
from app.api.v1.chat import router as chat_router
from app.core.security import get_current_user

api_v1_router = APIRouter(prefix="/api/v1")

# Auth routes — public (login/logout/me)
api_v1_router.include_router(auth_router)

# Read-only routes — public (support dashboard polling without auth)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(sites_router)
api_v1_router.include_router(operators_router)
api_v1_router.include_router(telemetry_router)
api_v1_router.include_router(anomalies_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(forecasts_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(impact_router)
api_v1_router.include_router(chat_router)

# Equipment — mixed: GET endpoints public, POST (add equipment) protected via endpoint decorator
api_v1_router.include_router(equipment_router)

# Mutation routes — require authentication via router-level dependency
api_v1_router.include_router(
    rentals_router,
    dependencies=[Depends(get_current_user)],
)
api_v1_router.include_router(
    actions_router,
    dependencies=[Depends(get_current_user)],
)
