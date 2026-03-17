# Suggested Features for OutbreakX

This document outlines potential features and improvements for the OutbreakX platform to enhance its capabilities in infectious disease surveillance and geospatial visualization.

## 1. Marker & Data Persistence
- **Sync Markers on Load**: Update the frontend to automatically fetch and display all existing markers from the FastAPI `/point/all` endpoint when the map initializes.
- **Marker Management**: Implement UI controls to edit or delete existing markers directly from the map interface.
- **Data Export**: Add functionality to export map data (markers, polygons, circles) in formats like GeoJSON or CSV for external analysis.

## 2. Advanced Geospatial Tools
- **Interactive Shape Drawing**: Integrate `leaflet-draw` or a similar library to allow users to draw Polygons, Circles, and Rectangles directly on the map and save them to the backend.
- **Proximity Alerts (Buffer Zones)**: Visualize "danger zones" by adding configurable buffer circles around active outbreak markers.
- **Point-to-Point Routing**: Utilize the existing FastAPI `p2p_routes` endpoint to visualize potential spread paths between two locations.

## 3. Visualization & Analytics
- **Disease Heatmaps**: Implement a heatmap layer to visualize high-density areas of reported cases, providing a clearer view of "hotspots."
- **Temporal Tracking (Timeline)**: Add a time-slider to visualize how an outbreak has spread over days, weeks, or months.
- **Categorization & Filtering**: Allow users to filter markers by disease type, severity level, or report date.

## 4. Search & Navigation
- **Geocoding & Search**: Add a search bar using a provider like OpenStreetMap's Nominatim to allow users to quickly navigate to specific cities or addresses.
- **Current Location**: Add a "Find My Location" button to center the map on the user's current GPS coordinates.

## 5. System & Infrastructure
- **Unified Backend**: Resolve the overlap between the Express and FastAPI backends by consolidating marker logic or clearly defining the responsibilities of each (e.g., Express for Auth/User Mgmt, FastAPI for heavy GIS processing).
- **Authentication**: Secure the platform with a login system to ensure only authorized personnel can add or modify outbreak data.
- **Real-time Updates**: Implement WebSockets (Socket.io) to push new markers to all connected clients instantly as they are reported.
