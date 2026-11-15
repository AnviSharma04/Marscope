"""
MARSCOPE Spatial Hazard Detection & Assessment Service
Differentiates Direct Observations (HiRISE, CTX, THEMIS) from Model-Derived Hazards.
"""

from services.elevation_service import haversine_distance_km, ElevationService

# Verified Mars Surface Hazards Catalog
KNOWN_HAZARDS = [
    {
        "id": "HAZ-001",
        "name": "Olympus Mons Basal Escarpment",
        "lat": 18.65,
        "lon": -133.80,
        "radius_km": 320.0,
        "type": "Steep Volcanic Scarp / Sheer Cliffs",
        "severity": 3,
        "category": "Observed Hazard",
        "evidence": "MOLA altimetry and HRSC imagery reveal 6-8 km vertical drop with cliff faces exceeding 35°.",
        "source_dataset": "MGS MOLA / Mars Express HRSC",
        "confidence": "High (Direct Altimetry)",
        "recommendation": "Impassable for astronaut EVA and wheeled rovers. Maintain minimum 15 km clearance."
    },
    {
        "id": "HAZ-002",
        "name": "Valles Marineris Wall Escarpments (Coprates Chasma)",
        "lat": -13.40,
        "lon": -59.20,
        "radius_km": 420.0,
        "type": "Deep Canyon Slopes / Landslide Chutes",
        "severity": 3,
        "category": "Observed Hazard",
        "evidence": "CTX mosaic and HiRISE stereo pairs document 5-9 km depth with slope angles 28°-42° and scree chutes.",
        "source_dataset": "MRO CTX / HiRISE",
        "confidence": "High (Direct Stereo Photogrammetry)",
        "recommendation": "Avoid canyon wall traverses; traverse strictly along canyon floor terraces."
    },
    {
        "id": "HAZ-003",
        "name": "Noctis Labyrinthus Fractured Graben Network",
        "lat": -7.00,
        "lon": -101.20,
        "radius_km": 280.0,
        "type": "Fractured Chaos / Extensional Fissures",
        "severity": 3,
        "category": "Observed Hazard",
        "evidence": "MRO THEMIS and CTX imagery show deep intersecting graben fissures, pit craters, and unstable rims.",
        "source_dataset": "2001 Mars Odyssey THEMIS / MRO CTX",
        "confidence": "High (Thermal & Visual Mapping)",
        "recommendation": "Severe fall and entrapment hazard. Navigational detours mandatory."
    },
    {
        "id": "HAZ-004",
        "name": "Jezero Crater Rim Crest (Western Scarp)",
        "lat": 18.45,
        "lon": 77.80,
        "radius_km": 25.0,
        "type": "Impact Crater Rim / Blocky Talus",
        "severity": 2,
        "category": "Observed Hazard",
        "evidence": "Perseverance SuperCam/Mastcam-Z and HiRISE digital terrain models indicate 18°-26° bouldery slopes.",
        "source_dataset": "Mars 2020 Perseverance / MRO HiRISE",
        "confidence": "Very High (In-Situ Rover + High-Res Orbital)",
        "recommendation": "Moderate slope; requires zig-zag ascent profile to stay under suit 20° limit."
    },
    {
        "id": "HAZ-005",
        "name": "Gale Crater Rim & Sharp Escarpment",
        "lat": -4.20,
        "lon": 137.30,
        "radius_km": 65.0,
        "type": "Crater Rim Crest / Aeolis Mons Flanks",
        "severity": 2,
        "category": "Observed Hazard",
        "evidence": "Curiosity MAHLI, ChemCam and HiRISE terrain models confirm 16°-24° layered outcrop scarps.",
        "source_dataset": "Curiosity MSL / MRO HiRISE",
        "confidence": "Very High (In-Situ Ground Truth)",
        "recommendation": "Requires designated ridge ascent corridors."
    },
    {
        "id": "HAZ-006",
        "name": "Jezero Séítah Dune Field (Sand Ripples)",
        "lat": 18.39,
        "lon": 77.41,
        "radius_km": 5.0,
        "type": "Active Megaripples / Regolith Sink Trap",
        "severity": 2,
        "category": "Observed Hazard",
        "evidence": "HiRISE imagery and Perseverance Navcam wheels sinkage: poorly sorted basaltic sand with high slip.",
        "source_dataset": "MRO HiRISE / Mars 2020 Mobility Logs",
        "confidence": "Very High (Rover In-Situ Verification)",
        "recommendation": "High wheel/boot sinkage risk. Traverses must circumvent megaripple troughs."
    },
    {
        "id": "HAZ-007",
        "name": "Hellas Planitia Low-Elevation Dust & Pressure Extremes",
        "lat": -42.40,
        "lon": 70.50,
        "radius_km": 650.0,
        "type": "Atmospheric Pressure & Regional Dust Storm Incubator",
        "severity": 2,
        "category": "Model-Derived Hazard",
        "evidence": "MGS TES and MRO MCS atmospheric profiles show surface pressure > 1150 Pa and frequent regional dust nucleation.",
        "source_dataset": "MGS TES / MRO Mars Climate Sounder (MCS)",
        "confidence": "Medium (Atmospheric Circulation Models)",
        "recommendation": "High risk of sudden optical opacity loss and dust accumulation on EVA solar/cooling units."
    },
    {
        "id": "HAZ-008",
        "name": "Elysium Mons Volcanic Slopes",
        "lat": 25.02,
        "lon": 147.21,
        "radius_km": 190.0,
        "type": "Volcanic Flank Incline / Lava Tubes",
        "severity": 2,
        "category": "Observed Hazard",
        "evidence": "THEMIS night-IR shows high thermal inertia lava flows and collapsed pit chains.",
        "source_dataset": "2001 Mars Odyssey THEMIS",
        "confidence": "High (Thermal Inertia Mapping)",
        "recommendation": "Watch for sub-surface void collapse and sharp basaltic pahoehoe ropes."
    },
    {
        "id": "HAZ-009",
        "name": "Nili Fossae Graben & Boulder Fields",
        "lat": 22.00,
        "lon": 75.00,
        "radius_km": 110.0,
        "type": "Tectonic Fractures & Meter-Scale Boulder Belts",
        "severity": 2,
        "category": "Observed Hazard",
        "evidence": "HiRISE meter-scale boulder counts show density > 15 boulders/100m² along fracture scarps.",
        "source_dataset": "MRO HiRISE (0.25 m/pixel)",
        "confidence": "High (Direct Feature Counts)",
        "recommendation": "Obstacle clearance required; unsuitable for motorized rover cart without scouting."
    }
]

class HazardService:
    @classmethod
    def get_all_hazards(cls):
        return KNOWN_HAZARDS

    @classmethod
    def hazards_at_location(cls, lat, lon):
        """
        Returns all mapped hazards intersecting the given point,
        plus dynamically checks for steep slope hazards from local MOLA DEM.
        """
        intersecting = []
        for h in KNOWN_HAZARDS:
            dist = haversine_distance_km(lat, lon, h["lat"], h["lon"])
            if dist <= h["radius_km"]:
                h_copy = dict(h)
                h_copy["dist_to_hazard_center_km"] = round(dist, 1)
                intersecting.append(h_copy)

        # Dynamic slope analysis from MOLA DEM
        slope_info = ElevationService.get_terrain_gradient_and_slope(lat, lon)
        slope = slope_info["slope_deg"]
        if slope >= 20.0:
            intersecting.append({
                "id": f"DYN-SLOPE-{int(abs(lat))}-{int(abs(lon))}",
                "name": f"Steep Slope Hazard ({slope}°)",
                "lat": lat,
                "lon": lon,
                "radius_km": 1.5,
                "type": "Critical Slope (> 20°)",
                "severity": 3,
                "category": "Model-Derived Hazard",
                "evidence": f"MOLA DEM gradient analysis calculated local terrain inclination of {slope}°, exceeding safe human EVA limit (20°).",
                "source_dataset": "MGS MOLA Gridded Elevation",
                "confidence": "Medium-High (Topographic Gradient)",
                "recommendation": "Exceeds suited astronaut walking limit. Path realignment required."
            })
        elif slope >= 12.0:
            intersecting.append({
                "id": f"DYN-CAUTION-{int(abs(lat))}-{int(abs(lon))}",
                "name": f"Elevated Gradient ({slope}°)",
                "lat": lat,
                "lon": lon,
                "radius_km": 1.5,
                "type": "Caution Slope (12°-20°)",
                "severity": 1,
                "category": "Model-Derived Hazard",
                "evidence": f"MOLA DEM slope analysis indicates {slope}° grade. Increases metabolic workload by ~45%.",
                "source_dataset": "MGS MOLA Gridded Elevation",
                "confidence": "Medium-High (Topographic Gradient)",
                "recommendation": "Traverse at reduced walking speed. Monitor suit oxygen consumption rate."
            })

        return intersecting

    @classmethod
    def check_route_hazards(cls, route_points):
        """
        Checks a sequence of route coordinates against all hazards and returns
        summary metrics and detected hazards.
        """
        detected_map = {}
        for pt in route_points:
            lat, lon = pt[0], pt[1]
            haz_list = cls.hazards_at_location(lat, lon)
            for h in haz_list:
                detected_map[h["name"]] = h

        return list(detected_map.values())
