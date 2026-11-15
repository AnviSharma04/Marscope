"""
MARSCOPE Backend: Planetary Exploration & Astronaut Mission Planning Server
NASA Space Apps Challenge 2026
Provides REST API endpoints for authentic Mars GIS data, multi-objective routing,
EVA simulation, digital twin telemetry, grounded AI assistant, and PDF dossiers.
"""

import os
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS

from config import MAP_LAYERS, ATTRIBUTION_STATEMENT, MARS_RADIUS_KM
from services.elevation_service import ElevationService, haversine_distance_km
from services.hazard_service import HazardService
from services.poi_service import PoiService
from services.routing_service import RoutingService
from services.eva_simulator import EvaSimulator
from services.digital_twin import DigitalTwinService
from services.assistant_service import AssistantService
from services.report_service import ReportService

app = Flask(__name__)
CORS(app)

# Ensure temporary directories exist
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(__file__), "scratch"))

@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Bad Request", message=str(e)), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify(error="Internal Server Error", message=str(e)), 500

@app.get("/api/health")
def health():
    return jsonify({
        "status": "online",
        "system": "MARSCOPE Planetary Exploration GIS Engine",
        "version": "2.0.0",
        "mars_geodetic_datum": "IAU Mars 2000 (R = 3389.5 km)",
        "disclaimer": ATTRIBUTION_STATEMENT
    })

@app.get("/api/layers")
def layers():
    """Returns available planetary map layers with full metadata and provenance."""
    return jsonify(list(MAP_LAYERS.values()))

@app.get("/api/pois")
def pois():
    """Returns catalog of authentic NASA mission science targets."""
    return jsonify(PoiService.get_all_pois())

@app.get("/api/hazards")
def hazards():
    """Returns catalog of verified Mars surface hazard regions."""
    return jsonify(HazardService.get_all_hazards())

@app.get("/api/location")
def location():
    """
    Returns terrain, elevation, slope, nearest feature, and local hazards for a coordinate point.
    """
    lat_raw = request.args.get("lat")
    lon_raw = request.args.get("lon")

    ok, coord = RoutingService.validate_coordinates(lat_raw, lon_raw)
    if not ok:
        return jsonify(error="Invalid coordinates", message=coord), 400

    lat, lon = coord
    elev = ElevationService.get_elevation_m(lat, lon)
    grad = ElevationService.get_terrain_gradient_and_slope(lat, lon)
    rough = ElevationService.get_terrain_roughness(lat, lon)
    terrain_type = ElevationService.classify_terrain(elev, grad["slope_deg"])

    nearest_poi, dist_km = PoiService.find_nearest_poi(lat, lon)
    local_hazards = HazardService.hazards_at_location(lat, lon)

    return jsonify({
        "lat": lat,
        "lon": lon,
        "elevation_m": elev,
        "slope_deg": grad["slope_deg"],
        "gradient": {
            "dz_dx": round(grad["dz_dx"], 4),
            "dz_dy": round(grad["dz_dy"], 4)
        },
        "roughness_index": rough["roughness_index"],
        "uncertainty_pct": rough["uncertainty_pct"],
        "terrain": terrain_type,
        "nearest_feature": nearest_poi["name"] if nearest_poi else "Unknown",
        "nearest_feature_type": nearest_poi["type"] if nearest_poi else "",
        "nearest_km": dist_km,
        "hazards": local_hazards,
        "environment": "MOLA Topographic Surface & THEMIS Thermal Context. Atmospheric surface pressure ~600-800 Pa.",
        "sources": [
            "https://trek.nasa.gov/mars/",
            "https://pds-geosciences.wustl.edu/missions/mgs/mola.htm",
            "https://themis.asu.edu/",
            "https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars"
        ]
    })

@app.get("/api/route")
def route():
    """
    Computes three terrain-aware multi-objective routes:
    1. Shortest
    2. Safest (slope & hazard penalty)
    3. Science-Optimized (detours to high-value targets)
    """
    g = request.args.get
    slat, slon = g("slat"), g("slon")
    elat, elon = g("elat"), g("elon")
    max_slope_str = g("max_slope", "20.0")

    # Validate presence
    if not slat or not slon or not elat or not elon:
        return jsonify({
            "error": "Missing required parameters",
            "message": "slat, slon, elat, and elon are all required query parameters."
        }), 400

    try:
        max_slope = float(max_slope_str)
    except ValueError:
        max_slope = 20.0

    try:
        routes = RoutingService.plan_routes(slat, slon, elat, elon, max_safe_slope=max_slope)
        return jsonify(routes)
    except ValueError as ve:
        return jsonify({"error": "Invalid route request", "message": str(ve)}), 400
    except Exception as ex:
        return jsonify({"error": "Route planning failure", "message": str(ex)}), 500

@app.post("/api/eva/simulate")
def eva_simulate():
    """
    Calculates astronaut life support budgets (O2, battery, water, weights, RTB margin).
    """
    body = request.get_json(silent=True) or {}
    route_data = body.get("route")
    if not route_data:
        return jsonify({"error": "Missing route", "message": "A valid route object is required."}), 400

    science_stops_minutes = float(body.get("science_stops_minutes", 0.0))
    custom_config = body.get("config", {})

    try:
        budget = EvaSimulator.calculate_mission_budget(route_data, science_stops_minutes, custom_config)
        return jsonify(budget)
    except Exception as ex:
        return jsonify({"error": "Simulation error", "message": str(ex)}), 500

@app.post("/api/digital_twin/telemetry")
def digital_twin_telemetry():
    """
    Calculates instantaneous mission state at a specified progress percentage.
    Supports scenario mutation (metabolic surge, obstacle blocking, extended stop).
    """
    body = request.get_json(silent=True) or {}
    route_data = body.get("route")
    if not route_data:
        return jsonify({"error": "Missing route", "message": "A valid route object is required."}), 400

    progress_pct = float(body.get("progress_pct", 0.0))
    scenario_injections = body.get("scenario_injections", {})

    try:
        telemetry = DigitalTwinService.simulate_telemetry_at_progress(route_data, progress_pct, scenario_injections)
        return jsonify(telemetry)
    except Exception as ex:
        return jsonify({"error": "Digital twin telemetry failure", "message": str(ex)}), 500

@app.post("/api/assistant/query")
def assistant_query():
    """
    Retrieval-augmented generation for scientific exploration questions.
    """
    body = request.get_json(silent=True) or {}
    question = body.get("question", "")
    if not question.strip():
        return jsonify({"error": "Empty question", "message": "Please provide a question string."}), 400

    context_lat = body.get("lat")
    context_lon = body.get("lon")
    active_route = body.get("route")

    try:
        if context_lat is not None and context_lon is not None:
            context_lat = float(context_lat)
            context_lon = float(context_lon)
    except (ValueError, TypeError):
        context_lat, context_lon = None, None

    result = AssistantService.query(question, context_lat, context_lon, active_route)
    return jsonify(result)

@app.post("/api/dossier/export")
def dossier_export():
    """
    Exports complete mission dossier in JSON or downloadable PDF format.
    """
    body = request.get_json(silent=True) or {}
    route_data = body.get("route")
    if not route_data:
        return jsonify({"error": "Missing route", "message": "Route data is required for dossier export."}), 400

    eva_budget = body.get("eva_budget")
    if not eva_budget:
        eva_budget = EvaSimulator.calculate_mission_budget(route_data)

    mission_meta = body.get("mission_meta", {})
    export_format = body.get("format", "json").lower()

    if export_format == "pdf":
        try:
            pdf_bytes = ReportService.generate_pdf_dossier(route_data, eva_budget, mission_meta)
            return Response(
                pdf_bytes,
                mimetype="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=MARSCOPE_Dossier_{mission_meta.get('mission_name', 'EVA')}.pdf"
                }
            )
        except Exception as ex:
            return jsonify({"error": "PDF generation failed", "message": str(ex)}), 500
    else:
        # JSON Export
        dossier = ReportService.generate_json_dossier(route_data, eva_budget, mission_meta)
        return jsonify(dossier)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
