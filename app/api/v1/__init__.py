"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import users, analysis

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router)
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])

# Add more routers as they are created:
# api_router.include_router(subscriptions.router)
# api_router.include_router(routines.router)
# api_router.include_router(products.router)
