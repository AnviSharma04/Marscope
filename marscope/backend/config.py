"""
MARSCOPE Configuration & Planetary Constants
Martian Geodetic Reference: IAU Mars 2000 Triaxial Ellipsoid / Spherical Approximation
"""

# Mars Planetary Physical Constants
MARS_RADIUS_KM = 3389.5          # Volumetric mean radius (km)
MARS_GRAVITY = 3.721             # Surface gravity (m/s^2), approx 0.38 Earth g
MARS_SOL_HOURS = 24.6597         # 24h 39m 35s

# Safe EVA Travel Thresholds (Human spacesuit operations)
MAX_SAFE_SLOPE_DEG = 20.0        # Traversible foot slope limit
WARNING_SLOPE_DEG = 12.0         # Caution slope threshold
NOMINAL_WALK_SPEED_KMH = 3.2     # Typical suited astronaut traverse speed on Mars regolith
ROVER_SCOUT_SPEED_KMH = 0.15     # Typical autonomous rover speed (e.g. Perseverance/Curiosity)

# NASA Mars Trek WMTS Tile Service Endpoints
TREK_BASE = "https://trek.nasa.gov/tiles/Mars/EQ/"
TREK_TILE_SUFFIX = "1.0.0/default/default028mm/{z}/{y}/{x}.jpg"

MAP_LAYERS = {
    "viking_mdim21": {
        "id": "viking_mdim21",
        "name": "NASA Viking MDIM 2.1 Color Mosaic",
        "mission": "Viking Orbiter 1 & 2",
        "instrument": "Visual Imaging Subsystem (VIS)",
        "type": "Global Visual Basemap",
        "url_template": f"{TREK_BASE}Mars_Viking_MDIM21_ClrMosaic_global_232m/{TREK_TILE_SUFFIX}",
        "max_zoom": 7,
        "resolution": "232 m/pixel",
        "coverage": "Global (100%)",
        "crs": "Equirectangular (EPSG:4326 / IAU Mars 2000)",
        "source_url": "https://trek.nasa.gov/mars/",
        "description": "Calibrated global color mosaic derived from Viking Orbiter clear, red, and violet filter images.",
        "limitations": "Historic imagery (1970s); lower spatial resolution than modern orbiter data."
    },
    "mola_elevation": {
        "id": "mola_elevation",
        "name": "MGS MOLA Color Shaded Relief & Elevation",
        "mission": "Mars Global Surveyor (MGS)",
        "instrument": "Mars Orbiter Laser Altimeter (MOLA)",
        "type": "Topography / Digital Elevation Model",
        "url_template": f"{TREK_BASE}Mars_MGS_MOLA_ClrShade_merge_global_463m/{TREK_TILE_SUFFIX}",
        "max_zoom": 6,
        "resolution": "463 m/pixel (128 pixels/degree)",
        "coverage": "Global (99.8%)",
        "crs": "Equirectangular (EPSG:4326 / IAU Mars 2000)",
        "source_url": "https://pds-geosciences.wustl.edu/missions/mgs/mola.htm",
        "description": "Planetary topographic datum established by laser altimeter pulses referenced to Martian gravitational geoid.",
        "limitations": "Footprint resolution 463m; cannot resolve sub-kilometer local obstacles or boulders."
    },
    "themis_day_ir": {
        "id": "themis_day_ir",
        "name": "Mars Odyssey THEMIS Daytime IR 100m Mosaic",
        "mission": "2001 Mars Odyssey",
        "instrument": "Thermal Emission Imaging System (THEMIS)",
        "type": "Thermal Infrared Mosaic (Band 9, 12.57 µm)",
        "url_template": f"{TREK_BASE}Mars_MO_THEMIS-IR-Day_mosaic_global_100m_v3/{TREK_TILE_SUFFIX}",
        "max_zoom": 8,
        "resolution": "100 m/pixel",
        "coverage": "Global (latitudes -60° to +60°)",
        "crs": "Equirectangular (EPSG:4326 / IAU Mars 2000)",
        "source_url": "https://themis.asu.edu/",
        "description": "Daytime surface brightness temperatures providing physical morphologic texture and sun-facing slopes.",
        "limitations": "Affected by atmospheric dust and atmospheric optical depth."
    },
    "themis_night_ir": {
        "id": "themis_night_ir",
        "name": "Mars Odyssey THEMIS Nighttime IR (Thermal Inertia)",
        "mission": "2001 Mars Odyssey",
        "instrument": "Thermal Emission Imaging System (THEMIS)",
        "type": "Nighttime Thermal Inertia Proxy",
        "url_template": f"{TREK_BASE}Mars_MO_THEMIS-IR-Night_mosaic_global_100m_v3/{TREK_TILE_SUFFIX}",
        "max_zoom": 8,
        "resolution": "100 m/pixel",
        "coverage": "Global",
        "crs": "Equirectangular (EPSG:4326 / IAU Mars 2000)",
        "source_url": "https://themis.asu.edu/",
        "description": "Nighttime thermal emission highlighting rock abundance versus fine sand/dust deposits.",
        "limitations": "Night temperature contrasts depend on seasonal variations."
    },
    "mro_ctx": {
        "id": "mro_ctx",
        "name": "MRO CTX Global Beta Mosaic",
        "mission": "Mars Reconnaissance Orbiter (MRO)",
        "instrument": "Context Camera (CTX)",
        "type": "Regional High-Resolution Context",
        "url_template": f"{TREK_BASE}Mars_MRO_CTX_mosaic_global_6m_v01/{TREK_TILE_SUFFIX}",
        "max_zoom": 12,
        "resolution": "6 m/pixel",
        "coverage": "Regional / Global Blended",
        "crs": "Equirectangular (EPSG:4326 / IAU Mars 2000)",
        "source_url": "https://mars.nasa.gov/mro/mission/instruments/ctx/",
        "description": "6-meter/pixel contextual morphology bridging orbiter overview and HiRISE meter-scale details.",
        "limitations": "Regional seams and varying illumination angles between camera passes."
    }
}

ATTRIBUTION_STATEMENT = (
    "MARSCOPE is an independent planetary exploration & mission planning system built for the NASA "
    "Space Apps Challenge 2026. Data products derived from NASA Mars Trek (Viking MDIM 2.1, MGS MOLA, "
    "Odyssey THEMIS, MRO CTX, HiRISE, CRISM) and USGS Planetary Geologic Mapping. Not certified for "
    "actual flight or operational astronaut navigation."
)
