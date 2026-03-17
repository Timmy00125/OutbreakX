from __future__ import annotations

import csv
import io
from datetime import date
from typing import Any, Optional, cast

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from geoalchemy2.shape import from_shape
from shapely import wkt
from shapely.geometry import Point
from sqlalchemy import func
from sqlalchemy.orm import Session

from config.database import get_db
from models import models
from schemas.dataclass import Coordinate
from schemas.schemas import (
    DiseaseCaseCreate,
    DiseaseCaseResponse,
    DiseaseImportResult,
    Location,
    DiseaseSummary,
)


router = APIRouter(prefix="/disease-cases")


def _to_response(item: models.DiseaseCase, db: Session) -> DiseaseCaseResponse:
    """Map ORM object into API response model with GeoJSON-style coordinates."""
    geom = cast(Point, wkt.loads(db.scalar(item.location_point.ST_AsText())))
    return DiseaseCaseResponse(
        id=cast(int, item.id),
        disease_name=cast(str, item.disease_name),
        location_name=cast(str, item.location_name),
        report_date=cast(date, item.report_date),
        case_count=cast(int, item.case_count),
        source=cast(Optional[str], item.source),
        severity_score=cast(Optional[float], item.severity_score),
        location=Location(
            type="Point",
            coordinates=Coordinate(longitude=geom.x, latitude=geom.y),
        ),
    )


def _parse_case_row(row: dict[str, Any], line_number: int) -> DiseaseCaseCreate:
    """Parse one CSV row into a validated disease case payload."""
    missing_fields = []
    for field in [
        "disease_name",
        "location_name",
        "report_date",
        "case_count",
        "latitude",
        "longitude",
    ]:
        if not row.get(field):
            missing_fields.append(field)

    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(f"line {line_number}: missing required fields ({missing})")

    try:
        return DiseaseCaseCreate(
            disease_name=str(row["disease_name"]).strip(),
            location_name=str(row["location_name"]).strip(),
            report_date=date.fromisoformat(str(row["report_date"]).strip()),
            case_count=int(str(row["case_count"]).strip()),
            latitude=float(str(row["latitude"]).strip()),
            longitude=float(str(row["longitude"]).strip()),
            source=(str(row.get("source", "")).strip() or None),
            severity_score=(
                float(str(row["severity_score"]).strip())
                if row.get("severity_score") not in (None, "")
                else None
            ),
        )
    except ValueError as exc:
        raise ValueError(f"line {line_number}: invalid field type ({exc})") from exc


@router.post("", response_model=DiseaseCaseResponse)
def create_disease_case(
    payload: DiseaseCaseCreate,
    db: Session = Depends(get_db),
) -> DiseaseCaseResponse:
    """Create a single disease case report."""
    if payload.case_count < 0:
        raise HTTPException(status_code=400, detail="case_count must be >= 0")

    db_item = models.DiseaseCase(
        disease_name=payload.disease_name,
        location_name=payload.location_name,
        report_date=payload.report_date,
        case_count=payload.case_count,
        source=payload.source,
        severity_score=payload.severity_score,
        location_point=from_shape(
            Point(payload.longitude, payload.latitude), srid=4326
        ),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return _to_response(db_item, db)


@router.post("/import/csv", response_model=DiseaseImportResult)
async def import_disease_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DiseaseImportResult:
    """Bulk import disease cases from CSV with row-level error reporting."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    raw_content = await file.read()
    decoded = raw_content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))

    required_columns = {
        "disease_name",
        "location_name",
        "report_date",
        "case_count",
        "latitude",
        "longitude",
    }
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file has no header")

    missing_columns = required_columns - set(reader.fieldnames)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise HTTPException(
            status_code=400,
            detail=f"Missing required CSV columns: {missing}",
        )

    imported = 0
    skipped = 0
    errors: list[str] = []

    for index, row in enumerate(reader, start=2):
        try:
            parsed = _parse_case_row(row, line_number=index)
            if parsed.case_count < 0:
                raise ValueError(f"line {index}: case_count must be >= 0")

            db_item = models.DiseaseCase(
                disease_name=parsed.disease_name,
                location_name=parsed.location_name,
                report_date=parsed.report_date,
                case_count=parsed.case_count,
                source=parsed.source,
                severity_score=parsed.severity_score,
                location_point=from_shape(
                    Point(parsed.longitude, parsed.latitude),
                    srid=4326,
                ),
            )
            db.add(db_item)
            imported += 1
        except ValueError as exc:
            skipped += 1
            errors.append(str(exc))

    db.commit()

    return DiseaseImportResult(imported=imported, skipped=skipped, errors=errors)


@router.get("", response_model=list[DiseaseCaseResponse])
def list_disease_cases(
    disease: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[DiseaseCaseResponse]:
    """List disease reports optionally filtered by disease name."""
    query = db.query(models.DiseaseCase)
    if disease:
        query = query.filter(
            func.lower(models.DiseaseCase.disease_name) == disease.lower()
        )

    items = query.order_by(models.DiseaseCase.report_date.desc()).all()
    return [_to_response(item, db) for item in items]


@router.get("/summary", response_model=DiseaseSummary)
def get_disease_summary(db: Session = Depends(get_db)) -> DiseaseSummary:
    """Return high-level totals and per-disease case counts."""
    total_reports = db.query(models.DiseaseCase).count()
    total_cases = (
        db.query(func.coalesce(func.sum(models.DiseaseCase.case_count), 0)).scalar()
        or 0
    )

    disease_rows = (
        db.query(
            models.DiseaseCase.disease_name,
            func.coalesce(func.sum(models.DiseaseCase.case_count), 0),
        )
        .group_by(models.DiseaseCase.disease_name)
        .order_by(models.DiseaseCase.disease_name.asc())
        .all()
    )
    disease_breakdown = {
        disease_name: int(case_sum) for disease_name, case_sum in disease_rows
    }

    return DiseaseSummary(
        total_reports=total_reports,
        total_cases=int(total_cases),
        disease_breakdown=disease_breakdown,
    )
