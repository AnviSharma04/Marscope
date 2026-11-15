"""
MARSCOPE Astronaut EVA and Survival Simulator
Biomechanical and life-support resource modeling under Martian gravity (0.38g).
Educational & mission-planning simulation model (not flight-certified life support).
"""

from config import MARS_GRAVITY

class EvaSimulator:
    """
    Simulates spacesuit consumable budgets (Oxygen, Battery Energy, Cooling Water)
    and evaluates mission return-to-base (RTB) feasibility.
    """

    # Default spacesuit parameters (Based on NASA Exploration Extravehicular Mobility Unit - xEMU baseline)
    DEFAULT_CONFIG = {
        "crew_size": 2,                     # Nominal buddy system (2 astronauts)
        "walking_speed_kmh": 3.2,           # Base suited traverse speed
        "suit_o2_capacity_liters": 1200.0,  # ~8.5 hours nominal capacity at standard metabolic rate
        "base_o2_rate_lpm": 1.4,            # Basal suited metabolic rate (Liters O2 / minute / astronaut)
        "battery_capacity_wh": 1400.0,      # Suit lithium-ion battery capacity
        "power_draw_watts": 175.0,          # Electronics, telemetry, fans, displays, avionics
        "cooling_water_kg": 4.5,            # Sublimator ice water mass
        "cooling_rate_kg_per_hour": 0.45,   # Sublimator water consumption under thermal load
        "equipment_mass_kg": 28.0,          # Scientific gear, spectrometers, core drill
        "sample_mass_kg": 12.0,             # Expected rock/regolith sample collection mass
        "astronaut_mass_kg": 80.0,          # Average suited astronaut body mass
        "suit_dry_mass_kg": 65.0,           # Exploration suit mass on Earth
        "safety_reserve_pct": 25.0,         # Minimum reserve requirement (rule of reserve)
        "max_allowable_eva_hours": 8.0      # NASA standard EVA duration cap
    }

    @classmethod
    def calculate_mission_budget(cls, route_data, science_stops_minutes=0.0, custom_config=None):
        """
        Calculates complete EVA consumables, weights, and RTB margins for a planned route.
        """
        cfg = dict(cls.DEFAULT_CONFIG)
        if custom_config:
            cfg.update(custom_config)

        crew_size = int(cfg.get("crew_size", 2))
        dist_km = float(route_data.get("distance_km", 0.0))
        avg_slope = float(route_data.get("avg_slope_deg", 0.0))
        max_slope = float(route_data.get("max_slope_deg", 0.0))

        # 1. Travel Time Analysis
        # Outbound time is half distance, return time is half distance
        est_walk_hours = float(route_data.get("estimated_duration_hours", dist_km / max(1.0, cfg["walking_speed_kmh"])))
        outbound_hours = round(est_walk_hours * 0.5, 2)
        return_hours = round(est_walk_hours * 0.5, 2)
        science_hours = round(float(science_stops_minutes) / 60.0, 2)
        total_eva_hours = round(outbound_hours + return_hours + science_hours, 2)

        # 2. Metabolic Rate Adjustments
        # Uphill walking and rough regolith increase oxygen consumption
        slope_metabolic_factor = 1.0 + (avg_slope / 15.0) * 0.45
        if max_slope > 18.0:
            slope_metabolic_factor += 0.25

        active_walk_minutes = est_walk_hours * 60.0
        stationary_science_minutes = science_stops_minutes

        o2_rate_active = cfg["base_o2_rate_lpm"] * slope_metabolic_factor
        o2_rate_stationary = cfg["base_o2_rate_lpm"] * 0.85 # Less exertion while sampling

        total_o2_per_astronaut_l = (active_walk_minutes * o2_rate_active) + (stationary_science_minutes * o2_rate_stationary)
        total_o2_crew_l = total_o2_per_astronaut_l * crew_size

        o2_capacity = cfg["suit_o2_capacity_liters"]
        o2_remaining_pct = max(0.0, round(((o2_capacity - total_o2_per_astronaut_l) / o2_capacity) * 100.0, 1))

        # 3. Battery Consumption
        # Watts * hours = Watt-hours
        battery_used_wh = total_eva_hours * cfg["power_draw_watts"]
        battery_cap = cfg["battery_capacity_wh"]
        battery_remaining_pct = max(0.0, round(((battery_cap - battery_used_wh) / battery_cap) * 100.0, 1))

        # 4. Cooling Sublimator Water
        cooling_used_kg = total_eva_hours * cfg["cooling_rate_kg_per_hour"]
        water_cap = cfg["cooling_water_kg"]
        water_remaining_pct = max(0.0, round(((water_cap - cooling_used_kg) / water_cap) * 100.0, 1))

        # 5. Mass & Weight on Mars (g = 3.721 m/s^2 vs Earth 9.806 m/s^2 -> ratio ~0.379)
        earth_g = 9.80665
        gravity_ratio = MARS_GRAVITY / earth_g

        cargo_earth_mass_kg = cfg["equipment_mass_kg"] + cfg["sample_mass_kg"]
        single_astronaut_earth_total_kg = cfg["astronaut_mass_kg"] + cfg["suit_dry_mass_kg"] + (cargo_earth_mass_kg / max(1, crew_size))

        cargo_mars_weight_n = cargo_earth_mass_kg * MARS_GRAVITY
        cargo_mars_weight_kg_equiv = round(cargo_earth_mass_kg * gravity_ratio, 1)

        single_astronaut_mars_weight_kg_equiv = round(single_astronaut_earth_total_kg * gravity_ratio, 1)

        # 6. Return-to-Base (RTB) Feasibility & Safety Checks
        reserve_threshold = cfg["safety_reserve_pct"]
        warnings = []
        is_rtb_feasible = True

        if total_eva_hours > cfg["max_allowable_eva_hours"]:
            warnings.append(f"Mission duration ({total_eva_hours} h) exceeds NASA 8.0-hour EVA physiological cap.")
            is_rtb_feasible = False

        if o2_remaining_pct < reserve_threshold:
            warnings.append(f"Oxygen reserve margin ({o2_remaining_pct}%) breached safe safety threshold ({reserve_threshold}%).")
            is_rtb_feasible = False

        if battery_remaining_pct < reserve_threshold:
            warnings.append(f"Battery energy reserve ({battery_remaining_pct}%) breached safe safety threshold ({reserve_threshold}%).")
            is_rtb_feasible = False

        if water_remaining_pct < reserve_threshold:
            warnings.append(f"Sublimator cooling water reserve ({water_remaining_pct}%) breached safe reserve ({reserve_threshold}%).")
            is_rtb_feasible = False

        if max_slope > 22.0:
            warnings.append(f"Peak terrain slope ({max_slope}°) exceeds spacesuit walking stability safety limits.")

        # Overall Status
        if not is_rtb_feasible:
            feasibility_status = "ABORT_REQUIRED / UNSAFE"
            recommendation = (
                "CRITICAL WARNING: Mission consumables or duration breach NASA safety thresholds. "
                "Reduce science stop duration, select the Safest route, or abort long-range waypoint traversal."
            )
        elif o2_remaining_pct < 35.0 or battery_remaining_pct < 35.0:
            feasibility_status = "FEASIBLE_WITH_CAUTION"
            recommendation = "Return-to-base is feasible. Moderate reserve margins; strictly adhere to science investigation timelines."
        else:
            feasibility_status = "NOMINAL_FEASIBLE"
            recommendation = "Mission plan is well within nominal life support consumable envelopes and NASA safety reserves."

        return {
            "is_rtb_feasible": is_rtb_feasible,
            "feasibility_status": feasibility_status,
            "recommendation": recommendation,
            "total_eva_hours": total_eva_hours,
            "outbound_hours": outbound_hours,
            "return_hours": return_hours,
            "science_hours": science_hours,
            "o2": {
                "consumed_per_astronaut_l": round(total_o2_per_astronaut_l, 1),
                "total_consumed_crew_l": round(total_o2_crew_l, 1),
                "capacity_l": o2_capacity,
                "remaining_pct": o2_remaining_pct,
                "reserve_threshold_pct": reserve_threshold
            },
            "battery": {
                "consumed_wh": round(battery_used_wh, 1),
                "capacity_wh": battery_cap,
                "remaining_pct": battery_remaining_pct,
                "reserve_threshold_pct": reserve_threshold
            },
            "cooling_water": {
                "consumed_kg": round(cooling_used_kg, 2),
                "capacity_kg": water_cap,
                "remaining_pct": water_remaining_pct,
                "reserve_threshold_pct": reserve_threshold
            },
            "mass_and_gravity": {
                "gravity_constant_mps2": MARS_GRAVITY,
                "gravity_earth_ratio": round(gravity_ratio, 3),
                "equipment_earth_mass_kg": cfg["equipment_mass_kg"],
                "sample_earth_mass_kg": cfg["sample_mass_kg"],
                "cargo_mars_weight_kg_equiv": cargo_mars_weight_kg_equiv,
                "astronaut_effective_weight_mars_kg": single_astronaut_mars_weight_kg_equiv
            },
            "warnings": warnings,
            "disclaimer": (
                "Educational and exploratory life-support mission model. Not certified for actual astronaut flight operations. "
                "Metabolic equations derived from NASA Apollo/xEMU engineering models."
            )
        }
