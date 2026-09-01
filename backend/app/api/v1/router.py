from fastapi import APIRouter
from app.api.v1.equipment import router as equipment_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.rentals import router as rentals_router
from app.api.v1.sites import router as sites_router
from app.api.v1.operators import router as operators_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(equipment_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(rentals_router)
api_v1_router.include_router(sites_router)
api_v1_router.include_router(operators_router)
