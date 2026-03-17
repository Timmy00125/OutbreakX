# Pydantic models
from datetime import date
from pydantic import BaseModel
from typing import Dict, Literal, List, Optional
from schemas.dataclass import Coordinate


class Location(BaseModel):
    type: Literal["Point"]
    coordinates: Coordinate


class PointCreate(BaseModel):
    location: Location
    description: str


class PointUpdate(BaseModel):
    location: Optional[Location] = None
    description: Optional[str] = None


class PolygonCoordinates(BaseModel):
    # A polygon is an array of coordinates (list of lists)
    coordinates: List[List[List[float]]]


class PolygonCreate(BaseModel):
    description: str
    geometry: PolygonCoordinates


class DiseaseCaseCreate(BaseModel):
    disease_name: str
    location_name: str
    report_date: date
    case_count: int
    latitude: float
    longitude: float
    source: Optional[str] = None
    severity_score: Optional[float] = None


class DiseaseCaseResponse(BaseModel):
    id: int
    disease_name: str
    location_name: str
    report_date: date
    case_count: int
    source: Optional[str] = None
    severity_score: Optional[float] = None
    location: Location


class DiseaseImportResult(BaseModel):
    imported: int
    skipped: int
    errors: List[str]


class DiseaseSummary(BaseModel):
    total_reports: int
    total_cases: int
    disease_breakdown: Dict[str, int]
