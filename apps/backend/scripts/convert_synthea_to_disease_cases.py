"""Convert Synthea CSV exports into OutbreakX disease case CSV format.

This script turns large raw Synthea data (patients + conditions) into a compact,
import-ready CSV that matches the `/disease-cases/import/csv` endpoint schema:

- disease_name
- location_name
- report_date
- case_count
- latitude
- longitude
- source
- severity_score
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple


REQUIRED_PATIENT_COLUMNS = {"Id", "CITY", "STATE", "LAT", "LON"}
REQUIRED_CONDITION_COLUMNS = {"START", "PATIENT", "DESCRIPTION"}
DEFAULT_DISEASE_PATTERN = r"(?i)covid|coronavirus|sars"
SOURCE_LABEL = "Synthea synthetic dataset"


@dataclass(frozen=True)
class PatientLocation:
    """Resolved patient location details from patients.csv."""

    location_name: str
    latitude: float
    longitude: float


@dataclass
class AggregateBucket:
    """Running aggregate used to calculate case count and average location."""

    case_count: int = 0
    latitude_sum: float = 0.0
    longitude_sum: float = 0.0


def parse_args() -> argparse.Namespace:
    """Build and parse CLI arguments for transformation options."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert Synthea CSVs to compact OutbreakX disease case CSV format."
        )
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Directory containing Synthea CSV files (patients.csv, conditions.csv).",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output CSV path for generated disease case records.",
    )
    parser.add_argument(
        "--disease-pattern",
        default=DEFAULT_DISEASE_PATTERN,
        help=(
            "Regex to filter condition descriptions. "
            "Default keeps COVID-like diseases only."
        ),
    )
    parser.add_argument(
        "--include-all-diseases",
        action="store_true",
        help="Include all condition descriptions and ignore --disease-pattern.",
    )
    parser.add_argument(
        "--collapse-covid-labels",
        action="store_true",
        help=(
            "Map COVID-like descriptions (e.g., Suspected COVID-19) into "
            "a single disease name: COVID-19."
        ),
    )
    parser.add_argument(
        "--time-bucket",
        choices=["day", "week", "month"],
        default="week",
        help="Aggregation granularity for report_date. Default: week.",
    )
    return parser.parse_args()


def _validate_required_columns(
    field_names: Optional[Iterable[str]],
    required_columns: set[str],
    file_name: str,
) -> None:
    """Validate required CSV headers and raise a clear error when missing."""
    if field_names is None:
        raise ValueError(f"{file_name} has no header row")

    missing_columns = required_columns - set(field_names)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(f"{file_name} missing required columns: {missing_list}")


def _normalize_location(city: str, state: str) -> str:
    """Create a stable human-readable location string from city/state."""
    city_clean = city.strip()
    state_clean = state.strip()
    if city_clean and state_clean:
        return f"{city_clean}, {state_clean}"
    if city_clean:
        return city_clean
    if state_clean:
        return state_clean
    return "Unknown"


def _bucket_date(report_date: date, bucket: str) -> date:
    """Reduce date granularity to day/week/month for compact reporting."""
    if bucket == "day":
        return report_date
    if bucket == "week":
        # ISO-style week bucket using Monday as anchor day.
        return report_date - timedelta(days=report_date.weekday())
    return report_date.replace(day=1)


def _normalize_disease_name(name: str, collapse_covid_labels: bool) -> str:
    """Optionally map variants of COVID labels to one canonical disease name."""
    normalized = name.strip()
    if not collapse_covid_labels:
        return normalized

    lowered = normalized.lower()
    if "covid" in lowered or "coronavirus" in lowered or "sars" in lowered:
        return "COVID-19"
    return normalized


def _parse_date(raw_value: str) -> date:
    """Parse Synthea condition date values safely (YYYY-MM-DD or ISO datetime)."""
    value = raw_value.strip()
    if not value:
        raise ValueError("empty date")

    # START often uses YYYY-MM-DD. Some exports may include timestamps.
    if "T" in value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    return date.fromisoformat(value[:10])


def load_patient_locations(patients_csv: Path) -> Dict[str, PatientLocation]:
    """Build patient_id -> location lookup used during condition aggregation."""
    patient_locations: Dict[str, PatientLocation] = {}

    with patients_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_required_columns(
            reader.fieldnames, REQUIRED_PATIENT_COLUMNS, "patients.csv"
        )

        for row in reader:
            patient_id = (row.get("Id") or "").strip()
            if not patient_id:
                continue

            try:
                latitude = float((row.get("LAT") or "").strip())
                longitude = float((row.get("LON") or "").strip())
            except ValueError:
                continue

            location_name = _normalize_location(
                city=(row.get("CITY") or ""),
                state=(row.get("STATE") or ""),
            )

            patient_locations[patient_id] = PatientLocation(
                location_name=location_name,
                latitude=latitude,
                longitude=longitude,
            )

    return patient_locations


def aggregate_conditions(
    conditions_csv: Path,
    patient_locations: Dict[str, PatientLocation],
    disease_pattern: Optional[re.Pattern[str]],
    collapse_covid_labels: bool,
    time_bucket: str,
) -> Tuple[Dict[Tuple[str, str, date], AggregateBucket], int, int]:
    """Aggregate condition rows into compact disease/location/date buckets."""
    aggregated: Dict[Tuple[str, str, date], AggregateBucket] = defaultdict(
        AggregateBucket
    )

    skipped_missing_location = 0
    skipped_filter = 0

    with conditions_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_required_columns(
            reader.fieldnames,
            REQUIRED_CONDITION_COLUMNS,
            "conditions.csv",
        )

        for row in reader:
            raw_description = (row.get("DESCRIPTION") or "").strip()
            if not raw_description:
                skipped_filter += 1
                continue

            if disease_pattern and not disease_pattern.search(raw_description):
                skipped_filter += 1
                continue

            patient_id = (row.get("PATIENT") or "").strip()
            patient_location = patient_locations.get(patient_id)
            if patient_location is None:
                skipped_missing_location += 1
                continue

            raw_start = (row.get("START") or "").strip()
            try:
                report_date = _bucket_date(_parse_date(raw_start), time_bucket)
            except ValueError:
                skipped_filter += 1
                continue

            disease_name = _normalize_disease_name(
                raw_description,
                collapse_covid_labels=collapse_covid_labels,
            )
            key = (
                disease_name,
                patient_location.location_name,
                report_date,
            )

            bucket = aggregated[key]
            bucket.case_count += 1
            bucket.latitude_sum += patient_location.latitude
            bucket.longitude_sum += patient_location.longitude

    return aggregated, skipped_missing_location, skipped_filter


def write_output_csv(
    output_csv: Path,
    aggregated: Dict[Tuple[str, str, date], AggregateBucket],
) -> int:
    """Write transformed aggregates in the exact schema expected by the API."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "disease_name",
                "location_name",
                "report_date",
                "case_count",
                "latitude",
                "longitude",
                "source",
                "severity_score",
            ],
        )
        writer.writeheader()

        for (disease_name, location_name, report_date), bucket in sorted(
            aggregated.items(),
            key=lambda item: (item[0][2], item[0][0], item[0][1]),
        ):
            if bucket.case_count <= 0:
                continue

            mean_latitude = bucket.latitude_sum / bucket.case_count
            mean_longitude = bucket.longitude_sum / bucket.case_count

            writer.writerow(
                {
                    "disease_name": disease_name,
                    "location_name": location_name,
                    "report_date": report_date.isoformat(),
                    "case_count": bucket.case_count,
                    "latitude": f"{mean_latitude:.6f}",
                    "longitude": f"{mean_longitude:.6f}",
                    "source": SOURCE_LABEL,
                    # No clinical severity in Synthea conditions export; leave blank.
                    "severity_score": "",
                }
            )
            rows_written += 1

    return rows_written


def main() -> int:
    """Run end-to-end transformation and print a concise summary."""
    args = parse_args()

    patients_csv = args.input_dir / "patients.csv"
    conditions_csv = args.input_dir / "conditions.csv"

    if not patients_csv.exists():
        raise FileNotFoundError(f"Missing file: {patients_csv}")
    if not conditions_csv.exists():
        raise FileNotFoundError(f"Missing file: {conditions_csv}")

    disease_pattern = None
    if not args.include_all_diseases:
        disease_pattern = re.compile(args.disease_pattern)

    patient_locations = load_patient_locations(patients_csv)

    aggregated, skipped_missing_location, skipped_filter = aggregate_conditions(
        conditions_csv=conditions_csv,
        patient_locations=patient_locations,
        disease_pattern=disease_pattern,
        collapse_covid_labels=args.collapse_covid_labels,
        time_bucket=args.time_bucket,
    )

    rows_written = write_output_csv(args.output, aggregated)

    print("Synthea conversion completed")
    print(f"Patient locations indexed: {len(patient_locations)}")
    print(f"Rows written: {rows_written}")
    print(f"Skipped (missing patient location): {skipped_missing_location}")
    print(f"Skipped (filter/date issues): {skipped_filter}")
    print(f"Output: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
