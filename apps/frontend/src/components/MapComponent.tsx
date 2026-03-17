import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import axios from "axios";
import "leaflet/dist/leaflet.css";

interface DiseaseLocation {
  type: "Point";
  coordinates:
    | [number, number]
    | { longitude: number; latitude: number }
    | { lng: number; lat: number };
}

interface DiseaseCase {
  id: number;
  disease_name: string;
  location_name: string;
  report_date: string;
  case_count: number;
  source?: string | null;
  severity_score?: number | null;
  location: DiseaseLocation;
}

interface DiseaseSummary {
  total_reports: number;
  total_cases: number;
  disease_breakdown: Record<string, number>;
}

const API_BASE = "http://localhost:8000";

function MapNavigator({
  target,
  zoom = 6,
}: {
  target: { lat: number; lng: number } | null;
  zoom?: number;
}): null {
  const map = useMap();

  useEffect(() => {
    if (!target) return;
    map.flyTo([target.lat, target.lng], zoom, { duration: 0.8 });
  }, [map, target, zoom]);

  return null;
}

function getMarkerColor(caseCount: number): string {
  if (caseCount >= 100) return "#b91c1c";
  if (caseCount >= 30) return "#ea580c";
  if (caseCount >= 10) return "#eab308";
  return "#0f766e";
}

function getNormalizedCoordinates(
  location: DiseaseLocation,
): { latitude: number; longitude: number } | null {
  const { coordinates } = location;

  if (Array.isArray(coordinates)) {
    const [longitude, latitude] = coordinates;
    if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
      return { latitude, longitude };
    }
    return null;
  }

  if (
    "longitude" in coordinates &&
    "latitude" in coordinates &&
    Number.isFinite(coordinates.latitude) &&
    Number.isFinite(coordinates.longitude)
  ) {
    return {
      latitude: coordinates.latitude,
      longitude: coordinates.longitude,
    };
  }

  if (
    "lat" in coordinates &&
    "lng" in coordinates &&
    Number.isFinite(coordinates.lat) &&
    Number.isFinite(coordinates.lng)
  ) {
    return {
      latitude: coordinates.lat,
      longitude: coordinates.lng,
    };
  }

  return null;
}

const MapComponent: React.FC = () => {
  const [diseaseCases, setDiseaseCases] = useState<DiseaseCase[]>([]);
  const [summary, setSummary] = useState<DiseaseSummary | null>(null);
  const [diseaseFilter, setDiseaseFilter] = useState<string>("");
  const [searchText, setSearchText] = useState<string>("");
  const [searchResult, setSearchResult] = useState<{
    lat: number;
    lng: number;
  } | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string>("");
  const [isBusy, setIsBusy] = useState<boolean>(false);

  const loadDiseaseCases = useCallback(async (disease: string) => {
    const response = await axios.get<DiseaseCase[]>(
      `${API_BASE}/disease-cases`,
      {
        params: disease ? { disease } : undefined,
      },
    );
    setDiseaseCases(response.data);
  }, []);

  const loadSummary = useCallback(async () => {
    const response = await axios.get<DiseaseSummary>(
      `${API_BASE}/disease-cases/summary`,
    );
    setSummary(response.data);
  }, []);

  const refreshData = useCallback(async () => {
    setIsBusy(true);
    setUploadMessage("");
    try {
      await Promise.all([loadDiseaseCases(diseaseFilter), loadSummary()]);
    } catch {
      setDiseaseCases([]);
      setSummary(null);
      setUploadMessage(
        "Unable to reach backend API. Ensure backend is running on port 8000.",
      );
    } finally {
      setIsBusy(false);
    }
  }, [diseaseFilter, loadDiseaseCases, loadSummary]);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const availableDiseases = useMemo(() => {
    if (!summary) return [];
    return Object.keys(summary.disease_breakdown);
  }, [summary]);

  const uploadCsv = async () => {
    if (!uploadFile) {
      setUploadMessage("Choose a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", uploadFile);

    setIsBusy(true);
    setUploadMessage("");

    try {
      const response = await axios.post<{
        imported: number;
        skipped: number;
        errors: string[];
      }>(`${API_BASE}/disease-cases/import/csv`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const { imported, skipped, errors } = response.data;
      const firstError = errors.length ? ` First error: ${errors[0]}` : "";
      setUploadMessage(
        `Import complete: ${imported} row(s) imported, ${skipped} skipped.${firstError}`,
      );
      setUploadFile(null);
      await Promise.all([loadDiseaseCases(diseaseFilter), loadSummary()]);
    } catch {
      setUploadMessage(
        "CSV import failed. Check file format and backend logs.",
      );
    } finally {
      setIsBusy(false);
    }
  };

  const searchLocation = async () => {
    const query = searchText.trim();
    if (!query) return;

    try {
      const response = await axios.get<Array<{ lat: string; lon: string }>>(
        "https://nominatim.openstreetmap.org/search",
        {
          params: { q: query, format: "json", limit: 1 },
        },
      );

      if (!response.data.length) return;
      const result = response.data[0];
      setSearchResult({ lat: Number(result.lat), lng: Number(result.lon) });
    } catch {
      setUploadMessage("Location search failed. Please try another place.");
    }
  };

  return (
    <div style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          top: "76px",
          left: "12px",
          zIndex: 1000,
          background: "rgba(255,255,255,0.96)",
          borderRadius: "10px",
          boxShadow: "0 3px 14px rgba(0,0,0,0.14)",
          padding: "12px",
          width: "min(420px, calc(100vw - 24px))",
        }}
      >
        <h3 style={{ margin: "0 0 8px", fontSize: "16px" }}>Disease Tracker</h3>
        <p style={{ margin: "0 0 12px", fontSize: "12px", color: "#475467" }}>
          Upload disease case CSV and visualize outbreaks by location.
        </p>

        <div style={{ display: "grid", gap: "8px", marginBottom: "10px" }}>
          <input
            type="file"
            accept=".csv"
            onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
          />
          <button
            onClick={uploadCsv}
            disabled={isBusy}
            style={{
              border: "none",
              borderRadius: "6px",
              background: "#0f766e",
              color: "#fff",
              padding: "8px 10px",
              cursor: "pointer",
            }}
          >
            Import Disease CSV
          </button>
        </div>

        <div style={{ display: "flex", gap: "8px", marginBottom: "10px" }}>
          <input
            value={searchText}
            onChange={(event) => setSearchText(event.target.value)}
            placeholder="Search city/address"
            style={{
              flex: 1,
              padding: "8px",
              borderRadius: "6px",
              border: "1px solid #d0d5dd",
            }}
          />
          <button
            onClick={searchLocation}
            style={{
              border: "none",
              borderRadius: "6px",
              background: "#1d4ed8",
              color: "#fff",
              padding: "8px 10px",
            }}
          >
            Search
          </button>
        </div>

        <div style={{ marginBottom: "10px" }}>
          <select
            value={diseaseFilter}
            onChange={(event) => setDiseaseFilter(event.target.value)}
            style={{
              width: "100%",
              padding: "8px",
              borderRadius: "6px",
              border: "1px solid #d0d5dd",
            }}
          >
            <option value="">All diseases</option>
            {availableDiseases.map((disease) => (
              <option key={disease} value={disease}>
                {disease}
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: "grid", gap: "6px", fontSize: "13px" }}>
          <div>
            <strong>Total reports:</strong> {summary?.total_reports ?? 0}
          </div>
          <div>
            <strong>Total cases:</strong> {summary?.total_cases ?? 0}
          </div>
          <div>
            <strong>Visible map points:</strong> {diseaseCases.length}
          </div>
        </div>

        {!!uploadMessage && (
          <div
            style={{
              marginTop: "10px",
              padding: "8px",
              borderRadius: "6px",
              background: "#f5f8ff",
              fontSize: "12px",
              color: "#1f2937",
            }}
          >
            {uploadMessage}
          </div>
        )}
      </div>

      <MapContainer
        center={[6.5244, 3.3792]}
        zoom={6}
        style={{ height: "100vh", width: "100%" }}
      >
        <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {diseaseCases.map((report) => {
          const coordinates = getNormalizedCoordinates(report.location);
          if (!coordinates) {
            return null;
          }

          const { latitude, longitude } = coordinates;
          const radius = Math.max(6, Math.min(20, report.case_count / 5));

          return (
            <CircleMarker
              key={report.id}
              center={[latitude, longitude]}
              radius={radius}
              pathOptions={{
                color: getMarkerColor(report.case_count),
                fillColor: getMarkerColor(report.case_count),
                fillOpacity: 0.5,
              }}
            >
              <Popup>
                <div style={{ minWidth: "220px" }}>
                  <h4 style={{ margin: "0 0 6px" }}>{report.disease_name}</h4>
                  <p style={{ margin: "0 0 5px" }}>
                    <strong>Location:</strong> {report.location_name}
                  </p>
                  <p style={{ margin: "0 0 5px" }}>
                    <strong>Cases:</strong> {report.case_count}
                  </p>
                  <p style={{ margin: "0 0 5px" }}>
                    <strong>Date:</strong> {report.report_date}
                  </p>
                  {report.source && (
                    <p style={{ margin: "0" }}>
                      <strong>Source:</strong> {report.source}
                    </p>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        <MapNavigator target={searchResult} />
      </MapContainer>
    </div>
  );
};

export default MapComponent;
