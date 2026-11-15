"""
MARSCOPE Mission Digital Twin & Scenario Intelligence Service
Simulates live Marswalk traverse progress, waypoint telemetry, and what-if mission anomalies.
"""

from services.elevation_service import haversine_distance_km, ElevationService
from services.hazard_service import HazardService
from services.poi_service import PoiService
from services.eva_simulator import EvaSimulator

class DigitalTwinService:
    @classmethod
    def simulate_telemetry_at_progress(cls, route_data, progress_pct, scenario_injections=None):
        """
        Calculates instantaneous mission state at progress_pct (0.0 to 100.0%).
        Supports active scenario mutations (e.g., metabolic spike, obstacle block, extended stop).
        """
        pts = route_data.get("points", [])
        if not pts:
            raise ValueError("Route contains no coordinate points.")

        progress_pct = max(0.0, min(100.0, float(progress_pct)))
        total_dist_km = float(route_data.get("distance_km", 0.0))
        total_eva_hours = float(route_data.get("estimated_duration_hours", 2.0))

        # Scenario adjustments
        scenario_injections = scenario_injections or {}
        o2_consumption_multiplier = float(scenario_injections.get("o2_multiplier", 1.0))
        extra_science_minutes = float(scenario_injections.get("extra_science_minutes", 0.0))
        blocked_waypoint_idx = scenario_injections.get("blocked_waypoint_index")
        emergency_rtb_active = scenario_injections.get("emergency_rtb", False)

        # 1. Waypoint interpolation
        n_pts = len(pts)
        if n_pts == 1 or progress_pct == 0.0:
            current_idx = 0
            curr_lat, curr_lon = pts[0][0], pts[0][1]
        elif progress_pct >= 100.0:
            current_idx = n_pts - 1
            curr_lat, curr_lon = pts[-1][0], pts[-1][1]
        else:
            fractional_idx = (progress_pct / 100.0) * (n_pts - 1)
            current_idx = int(fractional_idx)
            sub_t = fractional_idx - current_idx
            p1 = pts[current_idx]
            p2 = pts[min(n_pts - 1, current_idx + 1)]
            curr_lat = round(p1[0] + sub_t * (p2[0] - p1[0]), 5)
            curr_lon = round(p1[1] + sub_t * (p2[1] - p1[1]), 5)

        traversed_dist_km = round(total_dist_km * (progress_pct / 100.0), 2)
        remaining_dist_km = round(max(0.0, total_dist_km - traversed_dist_km), 2)

        elapsed_traverse_hours = round(total_eva_hours * (progress_pct / 100.0), 2)
        elapsed_total_hours = round(elapsed_traverse_hours + (extra_science_minutes / 60.0), 2)

        # Current terrain stats
        curr_elev = ElevationService.get_elevation_m(curr_lat, curr_lon)
        curr_slope_data = ElevationService.get_terrain_gradient_and_slope(curr_lat, curr_lon)
        curr_slope = curr_slope_data["slope_deg"]

        # Local hazards in immediate vicinity (< 10 km)
        nearby_hazards = HazardService.hazards_at_location(curr_lat, curr_lon)

        # Completed vs Pending Science Targets
        all_pois = route_data.get("pois", [])
        completed_pois = []
        pending_pois = []
        for p in all_pois:
            # Check distance from current location vs route origin
            d_curr = haversine_distance_km(curr_lat, curr_lon, p["lat"], p["lon"])
            if d_curr < 2.0 or progress_pct > 75.0:
                completed_pois.append(p)
            else:
                pending_pois.append(p)

        # Dynamic Resource consumption
        base_budget = EvaSimulator.calculate_mission_budget(route_data, science_stops_minutes=extra_science_minutes)
        nominal_o2_consumed = base_budget["o2"]["consumed_per_astronaut_l"] * (progress_pct / 100.0) * o2_consumption_multiplier
        nominal_battery_consumed = base_budget["battery"]["consumed_wh"] * (progress_pct / 100.0)
        nominal_water_consumed = base_budget["cooling_water"]["consumed_kg"] * (progress_pct / 100.0)

        o2_cap = base_budget["o2"]["capacity_l"]
        batt_cap = base_budget["battery"]["capacity_wh"]
        water_cap = base_budget["cooling_water"]["capacity_kg"]

        live_o2_remaining_pct = max(0.0, round(((o2_cap - nominal_o2_consumed) / o2_cap) * 100.0, 1))
        live_battery_remaining_pct = max(0.0, round(((batt_cap - nominal_battery_consumed) / batt_cap) * 100.0, 1))
        live_water_remaining_pct = max(0.0, round(((water_cap - nominal_water_consumed) / water_cap) * 100.0, 1))

        # Check RTB margin from current point to base
        # Return distance from current position to route start (waypoint 0)
        dist_to_base_km = round(haversine_distance_km(curr_lat, curr_lon, pts[0][0], pts[0][1]), 2)
        return_travel_hours = round(dist_to_base_km / 3.0, 2)
        o2_needed_for_return_l = return_travel_hours * 60.0 * 1.6
        o2_available_l = (live_o2_remaining_pct / 100.0) * o2_cap

        rtb_safe = o2_available_l >= (o2_needed_for_return_l * 1.25)

        # Recommended Action
        if emergency_rtb_active or not rtb_safe:
            recommended_action = "EMERGENCY RETURN TO BASE (RTB): Abort current science objectives. Follow direct bearing back to habitat."
            alert_level = "CRITICAL_ALERT"
        elif nearby_hazards:
            top_haz = nearby_hazards[0]
            recommended_action = f"CAUTION: Proximity to '{top_haz['name']}'. Reduce walking pace and maintain visual contact with buddy."
            alert_level = "WARNING"
        elif progress_pct >= 98.0:
            recommended_action = "DESTINATION REACHED: Secure science sample canisters and initiate habitat ingress checklist."
            alert_level = "NOMINAL"
        elif pending_pois and haversine_distance_km(curr_lat, curr_lon, pending_pois[0]["lat"], pending_pois[0]["lon"]) < 3.0:
            target_p = pending_pois[0]
            recommended_action = f"APPROACHING SCIENCE STOP: '{target_p['name']}'. Prepare Raman spectrometer and sample collection drill."
            alert_level = "SCIENCE_TARGET"
        else:
            recommended_action = f"PROCEED NOMINAL: Maintain course along azimuth towards Waypoint {min(n_pts - 1, current_idx + 1)}."
            alert_level = "NOMINAL"

        return {
            "progress_pct": progress_pct,
            "current_position": {
                "lat": curr_lat,
                "lon": curr_lon,
                "elevation_m": curr_elev,
                "slope_deg": curr_slope,
                "current_waypoint_index": current_idx,
                "total_waypoints": n_pts
            },
            "metrics": {
                "traversed_distance_km": traversed_dist_km,
                "remaining_distance_km": remaining_dist_km,
                "distance_to_base_km": dist_to_base_km,
                "elapsed_hours": elapsed_total_hours,
                "estimated_return_time_hours": return_travel_hours
            },
            "telemetry_gauges": {
                "oxygen": {
                    "remaining_pct": live_o2_remaining_pct,
                    "available_liters": round(o2_available_l, 1),
                    "rtb_required_liters": round(o2_needed_for_return_l, 1),
                    "is_nominal": live_o2_remaining_pct >= 25.0
                },
                "battery": {
                    "remaining_pct": live_battery_remaining_pct,
                    "is_nominal": live_battery_remaining_pct >= 25.0
                },
                "cooling_water": {
                    "remaining_pct": live_water_remaining_pct,
                    "is_nominal": live_water_remaining_pct >= 25.0
                }
            },
            "rtb_status": {
                "is_safe_to_return": rtb_safe,
                "return_point": pts[0]
            },
            "science_stops": {
                "completed": completed_pois,
                "pending": pending_pois
            },
            "nearby_hazards": nearby_hazards,
            "recommended_action": recommended_action,
            "alert_level": alert_level,
            "simulation_note": "Digital Twin representation for mission simulation and anomaly injection. Not live astronaut telemetry."
        }
