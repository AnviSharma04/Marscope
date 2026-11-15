# 🚀 MARSCOPE – Martian Exploration & Survival Companion

**Explore Smarter. Navigate Safer. Discover More.**

MARSCOPE is an interactive Mars exploration and route-planning application designed to help users understand the Martian surface and make informed decisions about potential exploration routes.

Developed as part of the **NASA Space Apps Challenge 2026**, MARSCOPE brings together planetary mapping, geographical information and pathfinding algorithms to demonstrate how future Mars exploration missions could approach surface navigation.

---

## 🌌 The Problem

Exploring Mars involves more than identifying a destination. Its varied terrain, steep slopes, craters and geological formations make route selection an important part of mission planning.

A route that appears shortest on a map may not necessarily be the most suitable one. MARSCOPE explores this problem by allowing users to compare different routes while considering estimated terrain conditions and mapped hazards.

## ✨ Key Features

### 1. Interactive Martian Map
- Explore the Martian surface using NASA Mars Trek imagery.
- Switch between Viking MDIM imagery and MOLA elevation layers.
- Zoom, pan and select locations on the map.
- View coordinates, estimated elevation and terrain classification for selected locations.

### 2. Terrain-Aware Route Planning
- Select a starting point and destination on the Martian map.
- Generate three route alternatives:
  - **Safest:** Uses the A* pathfinding algorithm with greater emphasis on avoiding steep terrain and mapped hazards.
  - **Balanced:** Uses a lower terrain and hazard penalty to balance route distance and conditions.
  - **Direct:** Displays a straight-line route between the selected locations.
- Compare approximate distance, maximum estimated slope and nearby hazards.

### 3. Hazard Identification
Explore curated hazard regions across Mars, including:
- Olympus Mons escarpment
- Valles Marineris canyon walls
- Noctis Labyrinthus fractures
- Hellas basin
- Gale Crater rim
- Jezero Crater rim
- Elysium Mons slopes

Hazard information includes location, estimated coverage radius, type and severity.

### 4. Scientific Points of Interest
Explore notable Martian geographical and scientific locations, including:
- Jezero Crater
- Gale Crater
- Mount Sharp
- Olympus Mons
- Valles Marineris
- Gusev Crater
- Meridiani Planum
- Hellas Planitia
- Elysium Planitia

Each location includes descriptive information and links to relevant scientific resources.

### 5. Mission Summary
Generate a summary of the selected route containing:
- Starting and ending coordinates
- Approximate distance
- Estimated maximum slope
- Number of route waypoints
- Mapped hazards along the route
- Nearby scientific points of interest

The summary can also be copied for reference.

---

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Frontend | Flutter, Dart |
| Backend | Python, Flask |
| Mapping | flutter_map, latlong2 |
| Map data | NASA Mars Trek |
| Route planning | A* pathfinding algorithm |
| API communication | HTTP, REST-style Flask endpoints |
| Cross-origin requests | Flask-CORS |

### Data Sources & References

MARSCOPE uses NASA and USGS resources for its planetary mapping and scientific references.

- [NASA Mars Trek](https://trek.nasa.gov/mars/) – Mars surface imagery and MOLA elevation map layers.
- [USGS Astrogeology](https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars) – Martian geological and geographical references.
- [NASA Mars 2020 Raw Images](https://mars.nasa.gov/mars2020/multimedia/raw-images/) – Perseverance mission imagery.
- [NASA – Curiosity's Proposed Path Up Mount Sharp](https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/) – Curiosity mission reference.

---

## ⚙️ Getting Started

Follow these steps to run MARSCOPE locally.

### Prerequisites

Make sure you have the following installed:

- [Flutter SDK](https://docs.flutter.dev/get-started/install)
- [Python 3](https://www.python.org/downloads/)
- pip (Python package manager)
- Git
- A browser or Android emulator

### 1. Clone the Repository

```bash
git clone https://github.com/AnviSharma04/Marscope.git
cd Marscope
```

### 2. Start the Backend

Open a terminal and navigate to the backend directory:

```bash
cd marscope/backend
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

The backend will run at:

`http://127.0.0.1
