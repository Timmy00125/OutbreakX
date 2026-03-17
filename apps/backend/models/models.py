from config.database import Base
from sqlalchemy import Column, Date, Float, Integer, String
from geoalchemy2 import Geometry


class Point(Base):
    __tablename__ = "shape"
    id = Column(Integer, primary_key=True, index=False)
    location_point = Column(Geometry(geometry_type="POINT", srid=4326))
    description = Column(String, index=True)


class DiseaseCase(Base):
    __tablename__ = "disease_case"

    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String, index=True, nullable=False)
    location_name = Column(String, index=True, nullable=False)
    report_date = Column(Date, index=True, nullable=False)
    case_count = Column(Integer, nullable=False)
    source = Column(String, nullable=True)
    severity_score = Column(Float, nullable=True)
    location_point = Column(Geometry(geometry_type="POINT", srid=4326))
