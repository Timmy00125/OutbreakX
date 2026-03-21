from fastapi import APIRouter
from api.endpoints.data import point  # Import the shapes router

from api.endpoints.data import file_upload
from api.endpoints.data import polygon
from api.endpoints.data import p2p_routes
from api.endpoints.data import circle
from api.endpoints.data import disease_cases
from api.endpoints import chat


router = APIRouter()

# data endpoints
router.include_router(point.router, tags=["POINT"])
router.include_router(polygon.router, tags=["POLYGON"])
router.include_router(p2p_routes.router, tags=["POINT TO POINT ROUTES"])
router.include_router(circle.router, tags=["CIRCLE"])
router.include_router(disease_cases.router, tags=["DISEASE CASES"])


# file upload endpoints
router.include_router(file_upload.router, tags=["FILE UPLOAD ENPOINTS"])

# chat endpoints
router.include_router(chat.router, prefix="/chat", tags=["CHAT"])
