from collections.abc import Generator
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, declarative_base, sessionmaker


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")


def get_ogr_pg_dsn() -> str:
    """Return DSN format expected by OGR2OGR tools."""
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    dbname = os.getenv("DB_NAME")
    password = os.getenv("DB_PASSWORD")

    if not all([host, user, dbname, password]):
        raise ValueError(
            "Missing DB config: "
            f"host={host}, user={user}, dbname={dbname}, "
            f"password={bool(password)}"
        )

    return f"host={host} user={user} dbname={dbname} password={password}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

print(f"Database engine created")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

try:
    with engine.connect() as connection:
        print("Successfully connected to the database!")
except Exception as e:
    print(f"Error connecting to the database: {e}")


def ensure_postgis_extension() -> None:
    """Ensure PostGIS is available before creating geometry-based tables."""
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    except SQLAlchemyError as exc:
        db_error = str(getattr(exc, "orig", exc))
        raise RuntimeError(
            "PostGIS extension is required but could not be enabled. "
            "Your PostgreSQL server likely does not have PostGIS installed. "
            "Install PostGIS on the DB server, or use the provided Docker DB "
            "service (postgis/postgis image), then run: "
            "CREATE EXTENSION IF NOT EXISTS postgis;. "
            f"Database error: {db_error}"
        ) from exc


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
