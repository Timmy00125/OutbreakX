# OutbreakX

OutbreakX is an open-source platform designed for **infectious disease surveillance**. It utilizes geospatial data to track and visualize disease outbreaks in real time, aiding public health efforts with detailed, accurate, and up-to-date location-based insights.

The platform leverages **FastAPI (Python), React (TypeScript), PostgreSQL with PostGIS,** and **OpenStreetMaps** to enable efficient data collection, analysis, and visualization of infectious disease patterns. An integrated **Gemini AI assistant** provides instant, evidence-based public health guidance directly within the application.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
  - [Import Sample Disease Data](#import-sample-disease-data)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Real-Time Outbreak Tracking**: Monitor infectious disease outbreaks with real-time geospatial data and visualizations on an interactive map.
- **Disease CSV Import**: Bulk upload disease case reports (`disease_name, location_name, report_date, case_count, latitude, longitude`) and track outbreaks immediately on the map.
- **Marker Management**: Create, edit, and delete outbreak markers directly on the map via interactive popups, with instant backend persistence.
- **Data Export**: Download map data in **GeoJSON** and **CSV** formats for external analysis in GIS or statistical tools.
- **Geospatial Analysis**: Powered by PostGIS, OutbreakX enables precise mapping, spatial queries, and proximity analysis of disease data.
- **Point-to-Point Routing**: Visualize potential disease spread paths between two locations.
- **Geospatial Shape Drawing**: Draw and save polygons, circles, and rectangles on the map to define zones of interest.
- **AI-Powered Health Assistant**: Integrated **Google Gemini** chatbot for evidence-based answers about diseases, epidemiological concepts, and public health guidance.
- **Search & Navigation**: Search for cities, addresses, or regions using OpenStreetMap's Nominatim geocoding service, plus a "Find My Location" button for field operatives.
- **OpenStreetMap Integration**: Free, open-source base maps for comprehensive mapping without proprietary dependencies.
- **API Access**: FastAPI backend with auto-generated OpenAPI docs allows seamless programmatic access to all data.

## Technologies

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18 (TypeScript), Leaflet, react-leaflet, Axios |
| **Backend** | FastAPI (Python 3), Uvicorn, SQLAlchemy, GeoAlchemy2, Shapely |
| **AI** | Google Gemini 2.5 Flash |
| **Database** | PostgreSQL with PostGIS extension |
| **Monorepo** | Turborepo, pnpm |
| **Maps** | OpenStreetMap (via Leaflet), Nominatim Geocoding |

## Getting Started

### Prerequisites

Ensure you have the following tools installed:

- **Node.js** (>= 18.x)
- **pnpm** ([installation guide](https://pnpm.io/installation))
- **Python** (>= 3.10)
- **PostgreSQL** with **PostGIS** extension

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Timmy00125/OutbreakX.git
   cd OutbreakX
   ```

2. **Install frontend and workspace dependencies**:

   ```bash
   pnpm install
   ```

3. **Install backend Python dependencies**:

   ```bash
   pip install -r apps/backend/requirements.txt
   ```

4. **Set up PostgreSQL and PostGIS**:

   Ensure PostgreSQL is running, then enable PostGIS on your database:

   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

5. **Configure Environment Variables**:

   Create a `.env` file in `apps/backend/` with the following variables:

   ```env
   DATABASE_URL=postgresql://user:password@host:5432/outbreakx
   GEMINI_API_KEY=your_gemini_api_key     # Required for AI chat
   ```

### Running the Project

#### Start Backend (FastAPI)

```bash
cd apps/backend
uvicorn main:app --reload --port 8000
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

#### Start Frontend (React)

```bash
pnpm --filter frontend dev
```

Opens at [http://localhost:3000](http://localhost:3000).

#### Start Full Project with Turborepo

```bash
pnpm run dev
```

This runs the frontend React server. Start the FastAPI backend separately as shown above.

### Import Sample Disease Data

Sample outbreak data is available in the `Data/` directory.

1. Start both backend and frontend.
2. Open the web app and use **Import Disease CSV** in the left control panel.
3. Select `Data/sample_disease_cases.csv`.
4. Review totals and disease breakdown on the map panel.

Additional test data is available in `Data/10k_synthea_covid19_csv/`.

## API Endpoints

### Disease Cases

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/disease-cases` | Create a single disease case report |
| `POST` | `/disease-cases/import/csv` | Bulk import disease reports from CSV |
| `GET` | `/disease-cases` | List disease reports (optional `?disease=Malaria`) |
| `GET` | `/disease-cases/summary` | Total reports, total cases, and per-disease breakdown |

### Map Points (Markers)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/point` | Create a new map marker |
| `GET` | `/point/all` | Get all map markers |
| `PUT` | `/point/{id}` | Update a marker's location or description |
| `DELETE` | `/point/{id}` | Delete a map marker |

### Geospatial Shapes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/polygon` | Create a polygon zone |
| `GET` | `/polygon/all` | Get all polygon zones |
| `DELETE` | `/polygon/{id}` | Delete a polygon zone |
| `POST` | `/circle` | Create a circular zone |
| `GET` | `/circle/all` | Get all circular zones |
| `DELETE` | `/circle/{id}` | Delete a circular zone |

### Routing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/p2p_routes` | Get a point-to-point route between two coordinates |

### AI Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message to the Gemini AI health assistant |
| `GET` | `/ping` | Health check endpoint |

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) for details on submitting pull requests and reporting issues. All interactions should follow our [Code of Conduct](docs/CODE_OF_CONDUCT.md).

## License

This project is licensed under the [ISC License](LICENSE).
