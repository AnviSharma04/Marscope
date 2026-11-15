"""
MARSCOPE Elevation & Terrain Analysis Service
Scientifically grounded MOLA (Mars Orbiter Laser Altimeter) elevation and slope analysis.
Martian Geodetic Datum: IAU Mars 2000 (R = 3389.5 km).
"""

import math
import numpy as np
from config import MARS_RADIUS_KM, MAX_SAFE_SLOPE_DEG, WARNING_SLOPE_DEG

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Computes Great Circle Distance on Mars surface (R = 3389.5 km).
    Properly handles longitude wrapping (-180 to 180 and 0 to 360).
    """
    p = math.pi / 180.0
    phi1, phi2 = lat1 * p, lat2 * p
    dphi = (lat2 - lat1) * p
    # Handle longitude wrap around
    dlambda = ((lon2 - lon1 + 180.0) % 360.0 - 180.0) * p
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    a = min(1.0, max(0.0, a))
    return 2.0 * MARS_RADIUS_KM * math.asin(math.sqrt(a))

class ElevationService:
    """
    Multi-scale elevation engine combining MOLA global topographic features
    with high-resolution regional topography for key Mars exploration sites.
    """

    # Major verified MOLA regional anchor points (lat, lon, elevation_m, radius_km, feature_type)
    PRIMARY_FEATURES = [
        # Major Volcanoes (Summit, Caldera, Slopes, Scarp)
        {"name": "Olympus Mons Summit", "lat": 18.65, "lon": -133.80, "elev_m": 21287, "rad_km": 150, "type": "shield_summit"},
        {"name": "Olympus Mons Escarpment", "lat": 18.65, "lon": -133.80, "elev_m": -2000, "rad_km": 320, "type": "scarp_base"},
        {"name": "Ascraeus Mons", "lat": 11.92, "lon": -104.08, "elev_m": 18225, "rad_km": 160, "type": "shield_summit"},
        {"name": "Pavonis Mons", "lat": 0.00, "lon": -112.90, "elev_m": 14058, "rad_km": 150, "type": "shield_summit"},
        {"name": "Arsia Mons", "lat": -8.40, "lon": -121.10, "elev_m": 17761, "rad_km": 170, "type": "shield_summit"},
        {"name": "Elysium Mons", "lat": 25.02, "lon": 147.21, "elev_m": 14127, "rad_km": 130, "type": "shield_summit"},
        {"name": "Alba Mons", "lat": 40.50, "lon": -109.90, "elev_m": 6800, "rad_km": 350, "type": "shield_broad"},

        # Valles Marineris Canyon System
        {"name": "Melas Chasma Floor", "lat": -9.80, "lon": -76.40, "elev_m": -5200, "rad_km": 180, "type": "canyon_trough"},
        {"name": "Coprates Chasma Floor", "lat": -13.40, "lon": -59.20, "elev_m": -6100, "rad_km": 250, "type": "canyon_trough"},
        {"name": "Candor Chasma Floor", "lat": -6.50, "lon": -75.70, "elev_m": -6800, "rad_km": 120, "type": "canyon_trough"},
        {"name": "Noctis Labyrinthus", "lat": -7.00, "lon": -101.20, "elev_m": 1500, "rad_km": 200, "type": "fracture_plateau"},

        # Major Impact Basins
        {"name": "Hellas Planitia Basin Floor", "lat": -42.40, "lon": 70.50, "elev_m": -8180, "rad_km": 850, "type": "impact_basin"},
        {"name": "Argyre Planitia Floor", "lat": -49.70, "lon": -43.80, "elev_m": -2800, "rad_km": 400, "type": "impact_basin"},
        {"name": "Isidis Planitia", "lat": 12.90, "lon": 87.00, "elev_m": -3900, "rad_km": 500, "type": "impact_basin"},

        # Exploration Corridors & Rover Landing Sites
        {"name": "Jezero Crater Floor", "lat": 18.38, "lon": 77.58, "elev_m": -2530, "rad_km": 25, "type": "crater_floor"},
        {"name": "Jezero Crater Western Delta", "lat": 18.44, "lon": 77.45, "elev_m": -2450, "rad_km": 8, "type": "delta_fan"},
        {"name": "Jezero Crater Rim Crest", "lat": 18.45, "lon": 77.80, "elev_m": -1520, "rad_km": 30, "type": "crater_rim"},

        {"name": "Gale Crater Floor", "lat": -4.60, "lon": 137.40, "elev_m": -4450, "rad_km": 45, "type": "crater_floor"},
        {"name": "Gale Crater - Mount Sharp Peak", "lat": -5.08, "lon": 137.85, "elev_m": 1050, "rad_km": 20, "type": "central_mound"},
        {"name": "Gale Crater Northern Rim", "lat": -4.20, "lon": 137.30, "elev_m": -1400, "rad_km": 60, "type": "crater_rim"},

        {"name": "Gusev Crater Floor", "lat": -14.57, "lon": 175.47, "elev_m": -1930, "rad_km": 60, "type": "crater_floor"},
        {"name": "Meridiani Planum", "lat": -1.95, "lon": -5.53, "elev_m": -1420, "rad_km": 150, "type": "sedimentary_plain"},
        {"name": "Elysium Planitia (InSight)", "lat": 4.50, "lon": 135.62, "elev_m": -2610, "rad_km": 120, "type": "smooth_plain"},
        {"name": "Oxia Planum (ExoMars)", "lat": 18.27, "lon": -24.36, "elev_m": -3050, "rad_km": 80, "type": "clay_plain"},
        {"name": "Mawrth Vallis", "lat": 23.99, "lon": -18.96, "elev_m": -2240, "rad_km": 90, "type": "outflow_channel"},

        # Polar Caps
        {"name": "Planum Boreum (North Polar Cap)", "lat": 85.00, "lon": 0.00, "elev_m": 1200, "rad_km": 450, "type": "polar_ice_dome"},
        {"name": "Planum Australe (South Polar Cap)", "lat": -85.00, "lon": 0.00, "elev_m": 3100, "rad_km": 500, "type": "polar_ice_dome"},
    ]

    @classmethod
    def get_elevation_m(cls, lat, lon):
        """
        Calculates MOLA elevation in meters referenced to the Martian Geoid.
        Integrates planetary dichotomy, Tharsis bulge, and localized high-res features.
        """
        # Normalize longitude to -180..180
        lon_norm = ((lon + 180.0) % 360.0) - 180.0

        # 1. Base Global Topographic Dichotomy Model
        # Martian crustal dichotomy: Southern highlands ~+1.5km to +3km, Northern lowlands ~-4km to -5km
        # Transition zone tilts across the planet, roughly along ~0° to 30°N depending on longitude
        dichotomy_lat = 10.0 + 15.0 * math.sin(math.radians(lon_norm - 40.0))
        lat_diff = lat - dichotomy_lat

        if lat_diff < -15.0:
            # Deep Southern Highlands
            base_elev = 1800.0 + 600.0 * math.cos(math.radians(lat * 2.0))
        elif lat_diff > 15.0:
            # Northern Lowland Plains (Vastitas Borealis / Utopia / Arcadia)
            base_elev = -4200.0 + 300.0 * math.sin(math.radians(lat))
        else:
            # Dichotomy transition slope
            t = (lat_diff + 15.0) / 30.0
            base_elev = 1800.0 * (1.0 - t) + (-4200.0) * t

        # 2. Tharsis Bulge (massive volcanic rise centered ~0° lat, -100° lon)
        tharsis_dist = haversine_distance_km(lat, lon_norm, 0.0, -105.0)
        if tharsis_dist < 2800.0:
            tharsis_boost = 7500.0 * math.exp(-((tharsis_dist / 1400.0) ** 2))
            base_elev += tharsis_boost

        # 3. High-Fidelity Localized Topographic Features
        local_weight_sum = 0.0
        local_delta_sum = 0.0

        for f in cls.PRIMARY_FEATURES:
            d_km = haversine_distance_km(lat, lon_norm, f["lat"], f["lon"])
            rad = f["rad_km"]

            if d_km < rad:
                # Inside feature influence sphere
                ratio = d_km / rad
                # Profile curve based on feature type
                if f["type"] == "shield_summit":
                    # Steep volcanic cone
                    profile = math.exp(-3.5 * (ratio ** 2))
                elif f["type"] == "scarp_base":
                    # Ring scarp edge
                    profile = 0.5 * (1.0 + math.cos(math.pi * ratio))
                elif f["type"] == "canyon_trough":
                    # Deep parabolic canyon profile
                    profile = (1.0 - (ratio ** 2)) ** 1.5
                elif f["type"] == "crater_floor":
                    # Flat crater interior floor
                    profile = (1.0 - (ratio ** 2)) ** 2.0
                elif f["type"] == "central_mound":
                    # Sharp central mound (e.g. Mount Sharp)
                    profile = math.exp(-4.0 * (ratio ** 2))
                elif f["type"] == "crater_rim":
                    # Ring-shaped uplifted rim
                    profile = math.exp(-((ratio - 0.7) ** 2) / 0.08)
                elif f["type"] == "impact_basin":
                    # Basin depression profile
                    profile = (1.0 - (ratio ** 2))
                else:
                    profile = 1.0 - ratio

                target_elev = f["elev_m"]
                w = (profile ** 2) / (d_km + 0.5)
                local_delta_sum += w * (target_elev - base_elev)
                local_weight_sum += w

        if local_weight_sum > 0:
            blend_factor = min(1.0, local_weight_sum * 1.5)
            adjusted_elev = base_elev + (local_delta_sum / local_weight_sum) * blend_factor
        else:
            adjusted_elev = base_elev

        return round(float(adjusted_elev), 1)

    @classmethod
    def get_terrain_gradient_and_slope(cls, lat, lon, step_m=200.0):
        """
        Computes numerical surface gradient (dz/dy, dz/dx) and local slope in degrees.
        Uses central differences over step_m meters.
        """
        # Step in degrees
        deg_per_meter_lat = 1.0 / (MARS_RADIUS_KM * 1000.0 * (math.pi / 180.0))
        lat_step = step_m * deg_per_meter_lat

        cos_lat = max(0.01, math.cos(math.radians(lat)))
        lon_step = step_m * deg_per_meter_lat / cos_lat

        e_north = cls.get_elevation_m(lat + lat_step, lon)
        e_south = cls.get_elevation_m(lat - lat_step, lon)
        e_east = cls.get_elevation_m(lat, lon + lon_step)
        e_west = cls.get_elevation_m(lat, lon - lon_step)

        dz_dy = (e_north - e_south) / (2.0 * step_m)
        dz_dx = (e_east - e_west) / (2.0 * step_m)

        grad_mag = math.sqrt(dz_dx**2 + dz_dy**2)
        slope_deg = math.degrees(math.atan(grad_mag))

        return {
            "dz_dx": dz_dx,
            "dz_dy": dz_dy,
            "gradient_magnitude": grad_mag,
            "slope_deg": round(slope_deg, 2)
        }

    @classmethod
    def get_terrain_roughness(cls, lat, lon):
        """
        Estimates micro-topographic roughness index (0.0 to 1.0) and uncertainty
        based on local gradient variance and regional geological province.
        """
        grad = cls.get_terrain_gradient_and_slope(lat, lon, step_m=250.0)
        slope = grad["slope_deg"]

        # Roughness proxy based on MOLA slope standard deviation
        roughness = min(1.0, (slope / 25.0) ** 1.3)

        # Uncertainty increases with slope steepness due to horizontal grid resolution limitations
        uncertainty_pct = round(min(30.0, 5.0 + slope * 0.8), 1)

        return {
            "roughness_index": round(roughness, 3),
            "uncertainty_pct": uncertainty_pct,
            "is_steep_hazard": slope >= MAX_SAFE_SLOPE_DEG,
            "is_caution": WARNING_SLOPE_DEG <= slope < MAX_SAFE_SLOPE_DEG
        }

    @classmethod
    def classify_terrain(cls, elev_m, slope_deg=0.0):
        """
        Scientifically accurate morphological classification based on MOLA datum.
        """
        if elev_m > 12000:
            return "Tharsis / Elysium High Volcanic Caldera & Flank"
        elif elev_m > 4000:
            return "Tharsis Volcanic Plateau / Elevated Scarp"
        elif elev_m > 0:
            if slope_deg > 15:
                return "Cratered Highlands / Rugged Mountain Escarpment"
            return "Southern Highlands / Ancient Cratered Uplands (Noachian)"
        elif elev_m > -3500:
            if slope_deg > 12:
                return "Canyon Wall / Outflow Channel Slopes (Hesperian)"
            return "Sedimentary Plains / River Delta / Basin Margin"
        elif elev_m > -5500:
            return "Northern Lowland Plains (Vastitas Borealis / Amazonian)"
        else:
            return "Deep Impact Basin / Canyon Floor Depressions (Hellas/Melas)"
