import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import axios from "axios";
import "leaflet/dist/leaflet.css";

interface MarkerData {
  id: number;
  location: {
    type: "Point";
    coordinates: [number, number];
  };
  description: string;
}

interface DescriptionDialogState {
  isOpen: boolean;
  position: { lat: number; lng: number } | null;
  description: string;
}

const API_BASE = "http://localhost:8000";

const icon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function MapNavigator({
  target,
  zoom = 14,
}: {
  target: { lat: number; lng: number } | null;
  zoom?: number;
}): null {
  const map = useMap();

  useEffect(() => {
    if (!target) {
      return;
    }
    map.flyTo([target.lat, target.lng], zoom, { duration: 0.8 });
  }, [map, target, zoom]);

  return null;
}

const MapEventHandler: React.FC<{
  onLeftClick: (lat: number, lng: number) => void;
  onRightClick: (args: {
    lat: number;
    lng: number;
    clientX: number;
    clientY: number;
  }) => void;
}> = ({ onLeftClick, onRightClick }) => {
  useMapEvents({
    click: (event) => {
      const { lat, lng } = event.latlng;
      onLeftClick(lat, lng);
    },
    contextmenu: (event) => {
      const { lat, lng } = event.latlng;
      onRightClick({
        lat,
        lng,
        clientX: event.originalEvent.clientX,
        clientY: event.originalEvent.clientY,
      });
      event.originalEvent.preventDefault();
    },
  });

  return null;
};

const MapComponent: React.FC = () => {
  const [markers, setMarkers] = useState<MarkerData[]>([]);
  const [isLoadingMarkers, setIsLoadingMarkers] = useState<boolean>(true);
  const [markerQuery, setMarkerQuery] = useState<string>("");
  const [rightClickPos, setRightClickPos] = useState<{
    lat: number;
    lng: number;
    clientX: number;
    clientY: number;
  } | null>(null);
  const [descriptionDialog, setDescriptionDialog] =
    useState<DescriptionDialogState>({
      isOpen: false,
      position: null,
      description: "",
    });
  const [editDialog, setEditDialog] = useState<{
    isOpen: boolean;
    markerId: number | null;
    description: string;
  }>({
    isOpen: false,
    markerId: null,
    description: "",
  });
  const [searchText, setSearchText] = useState<string>("");
  const [searchResult, setSearchResult] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  const visibleMarkers = useMemo(() => {
    const query = markerQuery.trim().toLowerCase();
    if (!query) {
      return markers;
    }
    return markers.filter((marker) =>
      marker.description.toLowerCase().includes(query),
    );
  }, [markers, markerQuery]);

  const loadMarkers = useCallback(async () => {
    setIsLoadingMarkers(true);
    try {
      const response = await axios.get<MarkerData[]>(`${API_BASE}/point/all`);
      setMarkers(response.data);
    } catch (error) {
      console.error("Error loading markers:", error);
      setMarkers([]);
    } finally {
      setIsLoadingMarkers(false);
    }
  }, []);

  useEffect(() => {
    loadMarkers();
  }, [loadMarkers]);

  const handleCreateMarker = async () => {
    if (!descriptionDialog.position || !descriptionDialog.description.trim()) {
      return;
    }

    const newMarker = {
      location: {
        type: "Point" as const,
        coordinates: [
          descriptionDialog.position.lng,
          descriptionDialog.position.lat,
        ] as [number, number],
      },
      description: descriptionDialog.description.trim(),
    };

    try {
      const response = await axios.post<MarkerData>(
        `${API_BASE}/point`,
        newMarker,
      );
      setMarkers((prevMarkers) => [...prevMarkers, response.data]);
      setDescriptionDialog({ isOpen: false, position: null, description: "" });
    } catch (error) {
      console.error("Error creating marker:", error);
    }
  };

  const openEditDialog = (marker: MarkerData) => {
    setEditDialog({
      isOpen: true,
      markerId: marker.id,
      description: marker.description,
    });
  };

  const handleUpdateMarker = async () => {
    if (!editDialog.markerId) {
      return;
    }

    try {
      const response = await axios.put<MarkerData>(
        `${API_BASE}/point/${editDialog.markerId}`,
        { description: editDialog.description.trim() },
      );

      setMarkers((prevMarkers) =>
        prevMarkers.map((marker) =>
          marker.id === editDialog.markerId ? response.data : marker,
        ),
      );

      setEditDialog({ isOpen: false, markerId: null, description: "" });
    } catch (error) {
      console.error("Error updating marker:", error);
    }
  };

  const handleDeleteMarker = async (markerId: number) => {
    try {
      await axios.delete(`${API_BASE}/point/${markerId}`);
      setMarkers((prevMarkers) =>
        prevMarkers.filter((marker) => marker.id !== markerId),
      );
    } catch (error) {
      console.error("Error deleting marker:", error);
    }
  };

  const exportMarkersAsGeoJson = () => {
    const geoJson = {
      type: "FeatureCollection",
      features: markers.map((marker) => ({
        type: "Feature",
        geometry: marker.location,
        properties: {
          id: marker.id,
          description: marker.description,
        },
      })),
    };

    const blob = new Blob([JSON.stringify(geoJson, null, 2)], {
      type: "application/geo+json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "outbreakx-markers.geojson";
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportMarkersAsCsv = () => {
    const headers = ["id", "longitude", "latitude", "description"];
    const rows = markers.map((marker) => [
      marker.id,
      marker.location.coordinates[0],
      marker.location.coordinates[1],
      `"${marker.description.replace(/"/g, '""')}"`,
    ]);
    const csv = [headers.join(","), ...rows.map((row) => row.join(","))].join(
      "\n",
    );

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "outbreakx-markers.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const findCurrentLocation = () => {
    if (!navigator.geolocation) {
      return;
    }

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setSearchResult({ lat: coords.latitude, lng: coords.longitude });
      },
      (error) => {
        console.error("Error fetching current location:", error);
      },
    );
  };

  const searchLocation = async () => {
    const query = searchText.trim();
    if (!query) {
      return;
    }

    try {
      const response = await axios.get<Array<{ lat: string; lon: string }>>(
        "https://nominatim.openstreetmap.org/search",
        {
          params: {
            q: query,
            format: "json",
            limit: 1,
          },
        },
      );

      if (!response.data.length) {
        return;
      }

      const result = response.data[0];
      setSearchResult({ lat: Number(result.lat), lng: Number(result.lon) });
    } catch (error) {
      console.error("Error searching location:", error);
    }
  };

  const markerCountLabel = isLoadingMarkers
    ? "Loading markers..."
    : `Markers: ${visibleMarkers.length} / ${markers.length}`;

  return (
    <div style={{ position: "relative" }}>
      <div
        style={{
          position: "absolute",
          top: "76px",
          left: "10px",
          zIndex: 1000,
          background: "rgba(255,255,255,0.96)",
          borderRadius: "8px",
          boxShadow: "0 2px 10px rgba(0,0,0,0.15)",
          padding: "10px",
          width: "min(360px, calc(100vw - 20px))",
        }}
      >
        <div style={{ marginBottom: "8px", fontSize: "14px", fontWeight: 700 }}>
          OutbreakX Tools
        </div>

        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
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
              background: "#0f7b6c",
              color: "#fff",
              padding: "8px 10px",
            }}
          >
            Search
          </button>
        </div>

        <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
          <button
            onClick={findCurrentLocation}
            style={{
              border: "1px solid #d0d5dd",
              borderRadius: "6px",
              background: "#fff",
              padding: "8px 10px",
            }}
          >
            Find My Location
          </button>
          <button
            onClick={exportMarkersAsGeoJson}
            style={{
              border: "1px solid #d0d5dd",
              borderRadius: "6px",
              background: "#fff",
              padding: "8px 10px",
            }}
          >
            Export GeoJSON
          </button>
          <button
            onClick={exportMarkersAsCsv}
            style={{
              border: "1px solid #d0d5dd",
              borderRadius: "6px",
              background: "#fff",
              padding: "8px 10px",
            }}
          >
            Export CSV
          </button>
        </div>

        <input
          value={markerQuery}
          onChange={(event) => setMarkerQuery(event.target.value)}
          placeholder="Filter markers by description"
          style={{
            width: "100%",
            padding: "8px",
            borderRadius: "6px",
            border: "1px solid #d0d5dd",
          }}
        />
        <div style={{ marginTop: "8px", fontSize: "12px", color: "#475467" }}>
          {markerCountLabel}
        </div>
      </div>

      <MapContainer
        center={[51.505, -0.09]}
        zoom={13}
        style={{ height: "100vh", width: "100%" }}
      >
        <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {visibleMarkers.map((marker) => (
          <Marker
            key={marker.id}
            position={[
              marker.location.coordinates[1],
              marker.location.coordinates[0],
            ]}
            icon={icon}
          >
            <Popup>
              <div style={{ minWidth: "220px" }}>
                <h4 style={{ margin: "0 0 8px 0" }}>Marker #{marker.id}</h4>
                <p style={{ margin: "0 0 12px 0" }}>
                  {marker.description || "No description"}
                </p>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => openEditDialog(marker)}
                    style={{
                      border: "1px solid #d0d5dd",
                      borderRadius: "6px",
                      background: "#fff",
                      padding: "6px 8px",
                    }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteMarker(marker.id)}
                    style={{
                      border: "none",
                      borderRadius: "6px",
                      background: "#b42318",
                      color: "#fff",
                      padding: "6px 8px",
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        <MapNavigator target={searchResult} />
        <MapEventHandler
          onLeftClick={(lat, lng) =>
            setDescriptionDialog({
              isOpen: true,
              position: { lat, lng },
              description: "",
            })
          }
          onRightClick={(position) => setRightClickPos(position)}
        />
      </MapContainer>

      {rightClickPos && (
        <div
          style={{
            position: "fixed",
            left: Math.min(rightClickPos.clientX + 10, window.innerWidth - 250),
            top: Math.min(rightClickPos.clientY + 10, window.innerHeight - 150),
            background: "white",
            padding: "15px",
            borderRadius: "8px",
            boxShadow: "0 3px 14px rgba(0,0,0,0.15)",
            zIndex: 1000,
            width: "220px",
            border: "1px solid #e0e0e0",
            fontFamily: "Arial, sans-serif",
          }}
        >
          <button
            onClick={() => setRightClickPos(null)}
            style={{
              position: "absolute",
              right: "8px",
              top: "8px",
              border: "none",
              background: "#f5f5f5",
              cursor: "pointer",
              padding: "4px 8px",
              borderRadius: "4px",
              color: "#666",
              fontSize: "14px",
            }}
          >
            X
          </button>

          <div style={{ marginBottom: "12px", paddingRight: "20px" }}>
            <h3
              style={{
                margin: "0 0 10px 0",
                color: "#333",
                fontSize: "16px",
                fontWeight: 600,
              }}
            >
              Location Details
            </h3>
          </div>

          <div
            style={{
              background: "#f8f9fa",
              padding: "10px",
              borderRadius: "6px",
              marginBottom: "12px",
            }}
          >
            <div style={{ marginBottom: "8px" }}>
              <label
                style={{
                  color: "#666",
                  fontSize: "12px",
                  display: "block",
                  marginBottom: "2px",
                }}
              >
                Latitude
              </label>
              <span
                style={{
                  color: "#333",
                  fontSize: "14px",
                  fontFamily: "monospace",
                }}
              >
                {rightClickPos.lat.toFixed(6)}
              </span>
            </div>

            <div>
              <label
                style={{
                  color: "#666",
                  fontSize: "12px",
                  display: "block",
                  marginBottom: "2px",
                }}
              >
                Longitude
              </label>
              <span
                style={{
                  color: "#333",
                  fontSize: "14px",
                  fontFamily: "monospace",
                }}
              >
                {rightClickPos.lng.toFixed(6)}
              </span>
            </div>
          </div>

          <button
            onClick={() =>
              navigator.clipboard.writeText(
                `${rightClickPos.lat},${rightClickPos.lng}`,
              )
            }
            style={{
              width: "100%",
              padding: "8px 12px",
              background: "#4a90e2",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: 500,
            }}
          >
            Copy Coordinates
          </button>
        </div>
      )}

      {descriptionDialog.isOpen && (
        <div
          style={{
            position: "fixed",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            background: "white",
            padding: "20px",
            borderRadius: "8px",
            boxShadow: "0 3px 14px rgba(0,0,0,0.15)",
            zIndex: 1000,
            width: "min(320px, calc(100vw - 20px))",
            border: "1px solid #e0e0e0",
          }}
        >
          <h3 style={{ margin: "0 0 15px 0" }}>Add Marker Description</h3>
          <textarea
            value={descriptionDialog.description}
            onChange={(event) =>
              setDescriptionDialog({
                ...descriptionDialog,
                description: event.target.value,
              })
            }
            style={{
              width: "100%",
              padding: "8px",
              marginBottom: "15px",
              borderRadius: "4px",
              border: "1px solid #ddd",
              minHeight: "100px",
              boxSizing: "border-box",
            }}
            placeholder="Enter description for this marker..."
          />
          <div
            style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}
          >
            <button
              onClick={() =>
                setDescriptionDialog({
                  isOpen: false,
                  position: null,
                  description: "",
                })
              }
              style={{
                padding: "8px 15px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                background: "white",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleCreateMarker}
              style={{
                padding: "8px 15px",
                background: "#4a90e2",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Add Marker
            </button>
          </div>
        </div>
      )}

      {editDialog.isOpen && (
        <div
          style={{
            position: "fixed",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            background: "white",
            padding: "20px",
            borderRadius: "8px",
            boxShadow: "0 3px 14px rgba(0,0,0,0.15)",
            zIndex: 1000,
            width: "min(320px, calc(100vw - 20px))",
            border: "1px solid #e0e0e0",
          }}
        >
          <h3 style={{ margin: "0 0 15px 0" }}>Edit Marker Description</h3>
          <textarea
            value={editDialog.description}
            onChange={(event) =>
              setEditDialog((prevState) => ({
                ...prevState,
                description: event.target.value,
              }))
            }
            style={{
              width: "100%",
              padding: "8px",
              marginBottom: "15px",
              borderRadius: "4px",
              border: "1px solid #ddd",
              minHeight: "100px",
              boxSizing: "border-box",
            }}
          />
          <div
            style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}
          >
            <button
              onClick={() =>
                setEditDialog({
                  isOpen: false,
                  markerId: null,
                  description: "",
                })
              }
              style={{
                padding: "8px 15px",
                border: "1px solid #ddd",
                borderRadius: "4px",
                background: "white",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleUpdateMarker}
              style={{
                padding: "8px 15px",
                background: "#0f7b6c",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Save
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapComponent;
