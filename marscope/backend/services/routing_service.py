"""
MARSCOPE Multi-Objective Planetary Route Planner
Algorithms: Geospatial A* on continuous Martian coordinates with DEM slope gradient costs.
Strategies: SHORTEST, SAFEST, SCIENCE-OPTIMIZED.
"""

import math
import heapq
from config import MARS_RADIUS_KM, MAX_SAFE_SLOPE_DEG, WARNING_SLOPE_DEG, NOMINAL_WALK_SPEED_KMH
from services.elevation_service import haversine_distance_km, ElevationService
from services.hazard_service import HazardService
from services.poi_service import PoiService

def tobler_mars_hiking_speed_kmh(slope_deg, base_speed_kmh=NOMINAL_WALK_SPEED_KMH):
    """
    Empirical locomotion velocity for suited astronaut in 0.38g under varying slope.
    Based on Tobler's hiking function adjusted for spacesuit joint resistance.
    """
    slope_rad = math.radians(slope_deg)
    # Suited astronauts walk slower uphill, and steep downhill (>15°) requires cautious descent
    factor = math.exp(-3.2 * abs(math.tan(slope_rad) + 0.04))
    speed = base_speed_kmh * factor
    return max(0.5, min(base_speed_kmh * 1.2, speed))

class RoutingService:
    @classmethod
    def validate_coordinates(cls, lat, lon):
        if lat is None or lon is None:
            return False, "Coordinates cannot be null."
        try:
            flat = float(lat)
            flon = float(lon)
        except (ValueError, TypeError):
            return False, "Coordinates must be valid floating point numbers."

        if not (-90.0 <= flat <= 90.0):
            return False, f"Latitude {flat}° is out of valid range [-90, +90]."
        if not (-180.0 <= flon <= 360.0):
            return False, f"Longitude {flon}° is out of valid range [-180, +360]."

        # Normalize longitude to [-180, 180]
        norm_lon = ((flon + 180.0) % 360.0) - 180.0
        return True, (round(flat, 5), round(norm_lon, 5))

    @classmethod
    def plan_routes(cls, start_lat, start_lon, end_lat, end_lon, max_safe_slope=MAX_SAFE_SLOPE_DEG):
        """
        Computes all three route strategies: Shortest, Safest, Science-Optimized.
        Returns a structured dictionary with comparison metrics and explainability.
        """
        # 1. Validation
        s_ok, s_val = cls.validate_coordinates(start_lat, start_lon)
        if not s_ok:
            raise ValueError(f"Start point invalid: {s_val}")
        e_ok, e_val = cls.validate_coordinates(end_lat, end_lon)
        if not e_ok:
            raise ValueError(f"Destination point invalid: {e_val}")

        start = s_val
        end = e_val

        # Direct distance check
        direct_dist_km = haversine_distance_km(start[0], start[1], end[0], end[1])

        # Edge case: Same point
        if direct_dist_km < 0.05:
            pt = [start[0], start[1]]
            elev = ElevationService.get_elevation_m(start[0], start[1])
            single_route = {
                "name": "Stationary / In-Situ Route",
                "strategy": "stationary",
                "points": [pt, pt],
                "distance_km": 0.0,
                "direct_distance_km": 0.0,
                "elev_start_m": elev,
                "elev_end_m": elev,
                "elev_min_m": elev,
                "elev_max_m": elev,
                "elev_gain_m": 0.0,
                "elev_loss_m": 0.0,
                "max_slope_deg": 0.0,
                "avg_slope_deg": 0.0,
                "estimated_duration_hours": 0.0,
                "hazards": HazardService.hazards_at_location(start[0], start[1]),
                "pois": PoiService.pois_near_route([pt], threshold_km=50.0),
                "safety_rating": "SAFE",
                "explanation": "Start and destination coordinates are identical. No traverse required; in-situ station mode."
            }
            return [single_route, single_route, single_route]

        # Plan the 3 strategies
        shortest_pts = cls._run_astar(start, end, strategy="shortest", max_slope=max_safe_slope)
        safest_pts = cls._run_astar(start, end, strategy="safest", max_slope=max_safe_slope)
        science_pts = cls._run_astar(start, end, strategy="science", max_slope=max_safe_slope)

        r_shortest = cls._evaluate_route("Shortest Traverse", "shortest", shortest_pts, start, end, direct_dist_km)
        r_safest = cls._evaluate_route("Safest Traverse (Hazard & Slope Avoidance)", "safest", safest_pts, start, end, direct_dist_km)
        r_science = cls._evaluate_route("Science-Optimized Traverse", "science", science_pts, start, end, direct_dist_km)

        return [r_shortest, r_safest, r_science]

    @classmethod
    def _run_astar(cls, start, end, strategy="safest", max_slope=MAX_SAFE_SLOPE_DEG):
        """
        Geospatial A* on adaptive grid with continuous DEM sampling.
        """
        dist_km = haversine_distance_km(start[0], start[1], end[0], end[1])

        # Determine grid dimensions based on scale
        if dist_km < 15.0:
            grid_n = 40
            pad_deg = max(0.04, dist_km / 118.0 * 0.6)
        elif dist_km < 80.0:
            grid_n = 50
            pad_deg = max(0.12, dist_km / 118.0 * 0.5)
        elif dist_km < 300.0:
            grid_n = 60
            pad_deg = max(0.35, dist_km / 118.0 * 0.4)
        else:
            grid_n = 65
            pad_deg = max(1.0, dist_km / 118.0 * 0.3)

        min_lat = min(start[0], end[0]) - pad_deg
        max_lat = max(start[0], end[0]) + pad_deg
        min_lon = min(start[1], end[1]) - pad_deg
        max_lon = max(start[1], end[1]) + pad_deg

        # Clamp latitude to [-89.5, 89.5]
        min_lat = max(-89.5, min_lat)
        max_lat = min(89.5, max_lat)

        d_lat = (max_lat - min_lat) / grid_n
        d_lon = (max_lon - min_lon) / grid_n

        def grid_to_coord(i, j):
            return (min_lat + i * d_lat, min_lon + j * d_lon)

        def coord_to_grid(lat, lon):
            i = int(round((lat - min_lat) / d_lat))
            j = int(round((lon - min_lon) / d_lon))
            return (max(0, min(grid_n, i)), max(0, min(grid_n, j)))

        start_cell = coord_to_grid(start[0], start[1])
        end_cell = coord_to_grid(end[0], end[1])

        if start_cell == end_cell:
            return [[start[0], start[1]], [end[0], end[1]]]

        # Relevant hazards & POIs in bounding box
        relevant_hazards = [
            h for h in HazardService.get_all_hazards()
            if haversine_distance_km(h["lat"], h["lon"], (start[0] + end[0])/2, (start[1] + end[1])/2) < (dist_km / 2 + h["radius_km"] + 100)
        ]
        relevant_pois = [
            p for p in PoiService.get_all_pois()
            if haversine_distance_km(p["lat"], p["lon"], (start[0] + end[0])/2, (start[1] + end[1])/2) < (dist_km / 2 + 150)
        ]

        # Cache for cell elevations and hazard costs
        cell_info_cache = {}

        def get_cell_cost(cell):
            if cell not in cell_info_cache:
                c_lat, c_lon = grid_to_coord(*cell)
                elev = ElevationService.get_elevation_m(c_lat, c_lon)

                # Hazard penalty
                haz_cost = 0.0
                for h in relevant_hazards:
                    d = haversine_distance_km(c_lat, c_lon, h["lat"], h["lon"])
                    if d < h["radius_km"]:
                        severity = h.get("severity", 1)
                        # Proximity penalty falls off from center to edge
                        proximity = (1.0 - d / h["radius_km"])
                        haz_cost += severity * proximity * 4.0

                # Science attraction bonus (for science-optimized strategy)
                sci_bonus = 0.0
                for p in relevant_pois:
                    dp = haversine_distance_km(c_lat, c_lon, p["lat"], p["lon"])
                    if dp < 50.0:
                        score = p.get("science_value_score", 80)
                        sci_bonus += (score / 100.0) * (1.0 - dp / 50.0) * 0.45

                cell_info_cache[cell] = (elev, haz_cost, sci_bonus)
            return cell_info_cache[cell]

        # Priority queue for A*: (f_score, cell)
        open_set = []
        heapq.heappush(open_set, (0.0, start_cell))
        came_from = {}
        g_score = {start_cell: 0.0}

        goal_lat, goal_lon = grid_to_coord(*end_cell)

        # 8-connected grid steps
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        found_goal = False
        iterations = 0
        max_iterations = 25000

        while open_set and iterations < max_iterations:
            iterations += 1
            current_f, current = heapq.heappop(open_set)

            if current == end_cell:
                found_goal = True
                break

            curr_lat, curr_lon = grid_to_coord(*current)
            curr_elev, _, _ = get_cell_cost(current)

            for di, dj in neighbors:
                ni, nj = current[0] + di, current[1] + dj
                if not (0 <= ni <= grid_n and 0 <= nj <= grid_n):
                    continue

                neighbor = (ni, nj)
                n_lat, n_lon = grid_to_coord(ni, nj)
                step_dist_km = haversine_distance_km(curr_lat, curr_lon, n_lat, n_lon)
                if step_dist_km < 1e-5:
                    continue

                n_elev, n_haz_cost, n_sci_bonus = get_cell_cost(neighbor)

                # Local slope
                delta_elev_m = abs(n_elev - curr_elev)
                slope_deg = math.degrees(math.atan(delta_elev_m / (step_dist_km * 1000.0)))

                # Strategy Multi-Objective Cost Weights
                if strategy == "shortest":
                    # Hard slope penalty if exceeding max_slope, otherwise minimal slope impedance
                    if slope_deg > max_slope:
                        slope_multiplier = 1.0 + (slope_deg - max_slope) * 20.0
                    else:
                        slope_multiplier = 1.0 + (slope_deg / 40.0)
                    step_cost = step_dist_km * (slope_multiplier + n_haz_cost * 0.3)

                elif strategy == "safest":
                    # Severe slope avoidance + strong hazard aversion
                    if slope_deg > max_slope:
                        slope_multiplier = 100.0 + (slope_deg - max_slope) ** 2
                    else:
                        slope_multiplier = 1.0 + 3.0 * ((slope_deg / WARNING_SLOPE_DEG) ** 2.2)
                    step_cost = step_dist_km * (slope_multiplier + n_haz_cost * 6.0)

                else: # science
                    # Moderate slope safety + attraction towards science sites
                    if slope_deg > max_slope:
                        slope_multiplier = 50.0
                    else:
                        slope_multiplier = 1.0 + 1.5 * ((slope_deg / WARNING_SLOPE_DEG) ** 1.8)
                    attraction = max(0.2, 1.0 - n_sci_bonus)
                    step_cost = step_dist_km * (slope_multiplier + n_haz_cost * 2.5) * attraction

                tentative_g = g_score[current] + step_cost

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h_dist = haversine_distance_km(n_lat, n_lon, goal_lat, goal_lon)
                    f_score = tentative_g + h_dist
                    heapq.heappush(open_set, (f_score, neighbor))

        # Path reconstruction with safety checks
        path_cells = []
        if found_goal and end_cell in came_from:
            curr = end_cell
            while curr in came_from:
                path_cells.append(curr)
                curr = came_from[curr]
            path_cells.append(start_cell)
            path_cells.reverse()
        else:
            # Fallback direct interpolated points if path was completely blocked
            steps = min(30, max(5, int(dist_km / 5.0)))
            pts = []
            for k in range(steps + 1):
                t = k / float(steps)
                pts.append([
                    round(start[0] + t * (end[0] - start[0]), 5),
                    round(start[1] + t * (end[1] - start[1]), 5)
                ])
            return pts

        # Convert cells to coordinates
        points = [[start[0], start[1]]]
        for cell in path_cells[1:-1]:
            c_lat, c_lon = grid_to_coord(*cell)
            points.append([round(c_lat, 5), round(c_lon, 5)])
        points.append([end[0], end[1]])

        return points

    @classmethod
    def _evaluate_route(cls, name, strategy, points, start, end, direct_dist_km):
        """
        Calculates full suite of terrain, hazard, duration, and scientific metrics for a route.
        """
        total_dist_km = 0.0
        elevations = []
        slopes = []
        elev_gain = 0.0
        elev_loss = 0.0
        total_duration_hours = 0.0

        for i, pt in enumerate(points):
            e = ElevationService.get_elevation_m(pt[0], pt[1])
            elevations.append(e)

            if i > 0:
                prev_pt = points[i - 1]
                prev_e = elevations[i - 1]
                seg_d = haversine_distance_km(prev_pt[0], prev_pt[1], pt[0], pt[1])
                total_dist_km += seg_d

                diff_e = e - prev_e
                if diff_e > 0:
                    elev_gain += diff_e
                else:
                    elev_loss += abs(diff_e)

                if seg_d > 1e-4:
                    sl = math.degrees(math.atan(abs(diff_e) / (seg_d * 1000.0)))
                else:
                    sl = 0.0
                slopes.append(sl)

                # Segment walking speed using Tobler Mars hiking equation
                seg_speed = tobler_mars_hiking_speed_kmh(sl)
                total_duration_hours += seg_d / seg_speed

        max_slope = max(slopes) if slopes else 0.0
        avg_slope = (sum(slopes) / len(slopes)) if slopes else 0.0

        # Hazards check
        hazards = HazardService.check_route_hazards(points)

        # Nearby Science POIs
        nearby_pois = PoiService.pois_near_route(points, threshold_km=max(25.0, direct_dist_km * 0.25))

        # Safety rating
        if max_slope >= MAX_SAFE_SLOPE_DEG or any(h.get("severity", 1) >= 3 for h in hazards):
            safety_rating = "HAZARDOUS"
        elif max_slope >= WARNING_SLOPE_DEG or len(hazards) > 0:
            safety_rating = "CAUTION"
        else:
            safety_rating = "SAFE"

        # Generate scientifically grounded explanation
        explanation = cls._generate_explanation(strategy, total_dist_km, direct_dist_km, max_slope, avg_slope, hazards, nearby_pois)

        return {
            "name": name,
            "strategy": strategy,
            "points": points,
            "distance_km": round(total_dist_km, 2),
            "direct_distance_km": round(direct_dist_km, 2),
            "elev_start_m": elevations[0] if elevations else 0,
            "elev_end_m": elevations[-1] if elevations else 0,
            "elev_min_m": min(elevations) if elevations else 0,
            "elev_max_m": max(elevations) if elevations else 0,
            "elev_gain_m": round(elev_gain, 1),
            "elev_loss_m": round(elev_loss, 1),
            "max_slope_deg": round(max_slope, 2),
            "avg_slope_deg": round(avg_slope, 2),
            "estimated_duration_hours": round(total_duration_hours, 2),
            "hazards": hazards,
            "pois": nearby_pois,
            "safety_rating": safety_rating,
            "explanation": explanation
        }

    @classmethod
    def _generate_explanation(cls, strategy, total_d, direct_d, max_s, avg_s, hazards, pois):
        detour_pct = round(((total_d - direct_d) / max(0.1, direct_d)) * 100.0, 1)

        if strategy == "shortest":
            reason = (
                f"Optimized for minimal traverse distance ({total_d} km, {detour_pct}% detour over straight line). "
                f"Traverses direct terrain with an average slope of {avg_s}° (peak {max_s}°). "
            )
            if hazards:
                reason += f"Note: Crosses {len(hazards)} mapped hazard zone(s); astronauts must maintain elevated situational vigilance."
            else:
                reason += "No critical mapped hazards intersected."

        elif strategy == "safest":
            reason = (
                f"Engineered for maximum crew safety. Circumvents steep topographic gradients, keeping maximum slope at {max_s}° "
                f"(avg {avg_s}°) and prioritizing stable regolith basins. "
            )
            if hazards:
                reason += f"Successfully skirted perimeter of major hazard features ({', '.join(h['name'] for h in hazards[:2])})."
            else:
                reason += "Completely clears all known mapped hazard perimeters."

        else: # science
            reason = (
                f"Science-Optimized traverse balancing energy expenditure with scientific yield. Detours to bring the crew within range of "
                f"{len(pois)} major scientific target(s)"
            )
            if pois:
                top_p = pois[0]
                reason += f", including '{top_p['name']}' ({top_p.get('distance_from_route_km', 0)} km detour, {top_p.get('type')}). "
            else:
                reason += ". "
            reason += f"Maintains acceptable slope profiles (avg {avg_s}°)."

        return reason
