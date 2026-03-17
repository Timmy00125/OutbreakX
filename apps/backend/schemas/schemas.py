# Pydantic models
from pydantic import BaseModel
from typing import Literal, List, Optional
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
