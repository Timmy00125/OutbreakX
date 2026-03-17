# api/endpoints/shapes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely import wkt
from shapely.geometry import Point
from models import models
from config.database import get_db
from schemas.schemas import PointCreate, PointUpdate
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from fastapi.logger import logger


router = APIRouter()


def point_to_response(shape: models.Point, db: Session):
    """Convert a DB point model to the frontend response shape."""
    geom = wkt.loads(db.scalar(shape.location_point.ST_AsText()))
    return {
        "id": shape.id,
        "location": {"type": "Point", "coordinates": [geom.x, geom.y]},
        "description": shape.description,
    }


@router.post("/point")
def create_shape(shape: PointCreate, db: Session = Depends(get_db)):
    try:
        if not shape.location.coordinates or len(shape.location.coordinates) != 2:
            logger.error("Location coordinates are missing")
            raise HTTPException(
                status_code=400,
                detail="Coordinates must contain exactly two values (longitude and latitude).",
            )
        lon, lat = shape.location.coordinates
        geom = Point(lon, lat)
        db_shape = models.Point(
            location_point=from_shape(geom, srid=4326), description=shape.description
        )
        db.add(db_shape)
        db.commit()
        db.refresh(db_shape)
        logger.info(f"Shape created with ID: {db_shape.id}")
        return point_to_response(db_shape, db)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/point/all")
def get_shapes(db: Session = Depends(get_db)):
    shapes = db.query(models.Point).all()
    return [point_to_response(shape, db) for shape in shapes]


@router.put("/point/{shape_id}")
def update_shape(shape_id: int, payload: PointUpdate, db: Session = Depends(get_db)):
    db_shape = db.query(models.Point).filter(models.Point.id == shape_id).first()
    if not db_shape:
        raise HTTPException(status_code=404, detail="Shape not found")

    try:
        if payload.location:
            if (
                not payload.location.coordinates
                or len(payload.location.coordinates) != 2
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Coordinates must contain exactly two values "
                        "(longitude and latitude)."
                    ),
                )
            lon, lat = payload.location.coordinates
            db_shape.location_point = from_shape(Point(lon, lat), srid=4326)

        if payload.description is not None:
            db_shape.description = payload.description

        db.commit()
        db.refresh(db_shape)
        return point_to_response(db_shape, db)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.delete("/point/{shape_id}")
def delete_shape(shape_id: int, db: Session = Depends(get_db)):
    db_shape = db.query(models.Point).filter(models.Point.id == shape_id).first()
    if not db_shape:
        raise HTTPException(status_code=404, detail="Shape not found")

    try:
        db.delete(db_shape)
        db.commit()
        return {"message": "Shape deleted", "id": shape_id}
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
