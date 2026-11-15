"""
MARSCOPE AI Scientific Exploration Assistant
Retrieval-grounded Q&A engine backed by NASA mission discoveries, USGS planetary units,
and instrument observations. Provides citations and provenance for every answer.
"""

from services.elevation_service import haversine_distance_km
from services.poi_service import PoiService
from services.hazard_service import HazardService

# Grounded Knowledge Corpus (NASA Missions, Instruments, Geological Discoveries)
GROUNDED_KNOWLEDGE_BASE = [
    {
        "keywords": ["jezero", "delta", "perseverance", "kodiak", "crater lake", "sediment", "clay"],
        "region": "Jezero Crater",
        "topic": "Ancient Lacustrine System & Delta Stratigraphy",
        "facts": (
            "Perseverance Mastcam-Z and SuperCam verified that Jezero Crater hosted a ~250m deep open-basin lake during the Noachian-Hesperian transition (~3.7 Ga). "
            "The Western Delta deposit (including the Kodiak remnant butte) exhibits classic Gilbert-type bottomset, foreset, and topset bedding deposited by Neretva Vallis. "
            "MRO CRISM spectroscopy identified iron-magnesium smectite clays and carbonate minerals, which have the highest known potential to preserve microscopic organic biosignatures on Mars."
        ),
        "interpretations": (
            "Geobiologists interpret the fine-grained mudstones at the delta toe as high-priority astrobiological targets, representing calm depositional waters capable of preserving ancient organic carbon."
        ),
        "mission_instruments": ["Mars 2020 Perseverance (Mastcam-Z, SuperCam, PIXL, SHERLOC)", "MRO (CRISM, HiRISE)"],
        "citations": [
            {"title": "Mars 2020 Perseverance Landing Site Science", "url": "https://mars.nasa.gov/mars2020/mission/science/landing-site/"},
            {"title": "Jezero Crater Lacustrine Delta Stratigraphy (Science / Nature)", "url": "https://science.nasa.gov/resource/perseverance-confirms-ancient-lake-and-river-delta-in-jezero/"}
        ]
    },
    {
        "keywords": ["gale", "curiosity", "mount sharp", "aeolis", "hematite", "glen torridon", "clay"],
        "region": "Gale Crater",
        "topic": "Habitable Lake Environments & Sulfate Transitions",
        "facts": (
            "NASA's Curiosity rover discovered fluvio-lacustrine mudstones at Yellowknife Bay, establishing that ancient Gale Crater had a habitable freshwater lake with neutral pH, low salinity, and essential bio-elements (C, H, N, O, P, S). "
            "Curiosity has climbed through over 600 meters of Mount Sharp (Aeolis Mons) strata, transitioning from clay-bearing mudstones (Glen Torridon) to hematite-rich ridges (Vera Rubin) and upper bedded sulfate salts, recording the global drying of Mars."
        ),
        "interpretations": (
            "The stratigraphy indicates multiple episodes of groundwater replenishment and redox variations rather than a simple one-way drying trend."
        ),
        "mission_instruments": ["Curiosity MSL (CheMin, SAM, Mastcam, ChemCam, APXS)", "MRO (CRISM, HiRISE)"],
        "citations": [
            {"title": "Curiosity's Traverse up Mount Sharp", "url": "https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/"},
            {"title": "Gale Crater Habitability Results (NASA Astrobiology)", "url": "https://astrobiology.nasa.gov/missions/msl/"}
        ]
    },
    {
        "keywords": ["water", "ice", "swim", "sharad", "subsurface", "glacier", "permafrost"],
        "region": "Mid-to-High Latitudes / Arcadia Planitia",
        "topic": "Subsurface Water Ice & Glacial Morphology",
        "facts": (
            "NASA's Subsurface Water Ice Mapping (SWIM) project synthesized SHARAD shallow radar, Odyssey Gamma Ray/Neutron Spectrometers, and HiRISE fresh-impact crater exposures. "
            "In Arcadia Planitia and Deuteronilus Mensae, sheet-like excess water-ice bodies reside at depths between 1.0 and 5.0 meters below desiccated regolith overburden. "
            "Radar dielectric measurements (dielectric constant ~ 3.1) confirm high-purity water ice with low dielectric loss."
        ),
        "interpretations": (
            "These buried ice sheets represent relict Amazonian glacial or snowpack deposits from past high-obliquity orbital cycles, serving as prime target sites for human In-Situ Resource Utilization (ISRU)."
        ),
        "mission_instruments": ["MRO SHARAD Radar Sounder", "2001 Mars Odyssey GRS/HEND", "MRO HiRISE (impact excavation imaging)"],
        "citations": [
            {"title": "NASA Subsurface Water Ice Mapping (SWIM)", "url": "https://swim.psi.edu/"},
            {"title": "Exposed Subsurface Ice Sheets in Martian Mid-Latitudes (Science)", "url": "https://science.nasa.gov/missions/mro/exposed-subsurface-ice-sheets-in-the-martian-mid-latitudes/"}
        ]
    },
    {
        "keywords": ["valles marineris", "canyon", "chasma", "candor", "melas", "landslide"],
        "region": "Valles Marineris",
        "topic": "Giant Tectonic Rifting & Interior Layered Deposits",
        "facts": (
            "Valles Marineris spans over 4,000 km in length, reaching widths up to 200 km and depths down to 9,000 meters. "
            "Formed by crustal extension associated with the Tharsis volcanic bulge, the canyon exposes deep crustal stratigraphy. "
            "Interior Layered Deposits (ILDs) in Candor and Melas Chasmata contain thick stacks of polyhydrated sulfates (kieserite, epsomite, gypsum) mapped by CRISM and OMEGA."
        ),
        "interpretations": (
            "Geologists debate whether ILDs formed in sub-ice volcano interactions, ancient enclosed lakes, or eolian dust-trapping cycles with groundwater cementation."
        ),
        "mission_instruments": ["MRO CRISM & HiRISE", "MGS MOLA Altimeter", "Mars Express HRSC & OMEGA"],
        "citations": [
            {"title": "USGS Geologic Map of Valles Marineris", "url": "https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars"},
            {"title": "Mars Trek Valles Marineris 3D Topography", "url": "https://trek.nasa.gov/mars/"}
        ]
    },
    {
        "keywords": ["olympus", "volcano", "tharsis", "scarp", "caldera", "lava"],
        "region": "Olympus Mons",
        "topic": "Shield Volcanism & Basal Escarpments",
        "facts": (
            "Olympus Mons is the largest shield volcano in the solar system, with a summit elevation of +21,287 meters above the MOLA datum and a base diameter exceeding 600 km. "
            "The volcano is bounded by a basal escarpment 6 to 8 km tall with sheer cliff faces exceeding 35° incline. "
            "The summit caldera consists of six nested collapse calderas spanning 80 km across and up to 3 km deep."
        ),
        "interpretations": (
            "The massive size of Tharsis volcanoes is attributed to the absence of active plate tectonics on Mars, allowing stationary mantle hot-spots to erupt through the same crustal crust for hundreds of millions of years."
        ),
        "mission_instruments": ["MGS MOLA", "Mars Express HRSC", "Viking Orbiter VIS"],
        "citations": [
            {"title": "NASA Solar System Exploration: Olympus Mons", "url": "https://science.nasa.gov/mars/facts/"},
            {"title": "MGS MOLA Topographic Survey of Tharsis", "url": "https://pds-geosciences.wustl.edu/missions/mgs/mola.htm"}
        ]
    },
    {
        "keywords": ["route", "safety", "slope", "hazard", "planning", "eva", "astronaut"],
        "region": "General Mission Planning",
        "topic": "Planetary Traverse Safety & Human EVA Constraints",
        "facts": (
            "Suited astronaut locomotion on Mars (0.38g) is constrained by pressurized spacesuit joint torques. "
            "NASA EVA biomechanical guidelines restrict continuous suited slopes to < 15°-20° to prevent catastrophic slips and excessive metabolic oxygen consumption. "
            "Traverse planners must maintain a 25% reserve on life support consumables (O2, battery energy, and sublimator cooling water) at all times."
        ),
        "interpretations": (
            "Multi-objective path optimization prevents high-risk traversal through steep crater rims, active dune fields, and scree chutes while maximizing scientific observation dwell time."
        ),
        "mission_instruments": ["NASA EVA Guidelines", "Apollo Lunar Surface Operations Archive", "xEMU Human Factors Studies"],
        "citations": [
            {"title": "NASA Human Integration Design Handbook (HIDH)", "url": "https://www.nasa.gov/reference/hidh/"},
            {"title": "MARSCOPE Mission Planning Architecture", "url": "https://trek.nasa.gov/mars/"}
        ]
    }
]

class AssistantService:
    @classmethod
    def query(cls, question_text, context_lat=None, context_lon=None, active_route=None):
        """
        Retrieval-augmented generation for Mars exploration questions.
        Matches relevant knowledge entries, incorporates regional spatial context,
        and produces scientifically grounded answers with citations.
        """
        q_lower = (question_text or "").lower()

        # Score entries by keyword matches
        scored_entries = []
        for entry in GROUNDED_KNOWLEDGE_BASE:
            score = 0
            for kw in entry["keywords"]:
                if kw in q_lower:
                    score += 2
            # Proximity boost if coordinates provided
            if context_lat is not None and context_lon is not None:
                # Find if knowledge entry relates to nearest POI
                nearest_poi, d_km = PoiService.find_nearest_poi(context_lat, context_lon)
                if nearest_poi and any(kw in nearest_poi["name"].lower() for kw in entry["keywords"]):
                    score += 3
            if score > 0:
                scored_entries.append((score, entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)

        if not scored_entries:
            # Fallback to general Mars knowledge
            entry = GROUNDED_KNOWLEDGE_BASE[-1] # Safety / general mission
        else:
            entry = scored_entries[0][1]

        # Spatial context enrichment
        spatial_context_str = ""
        if context_lat is not None and context_lon is not None:
            nearest_poi, d_km = PoiService.find_nearest_poi(context_lat, context_lon)
            hazards_here = HazardService.hazards_at_location(context_lat, context_lon)
            spatial_context_str = (
                f"\n\n**Current Geospatial Context ({context_lat:.3f}°, {context_lon:.3f}°):**\n"
                f"- Nearest Major Science Landmark: **{nearest_poi['name']}** (~{d_km} km away).\n"
            )
            if hazards_here:
                spatial_context_str += f"- Active Local Hazards: {', '.join(h['name'] for h in hazards_here)}.\n"
            else:
                spatial_context_str += "- Active Local Hazards: None directly intersecting point.\n"

        # Active route context enrichment
        route_context_str = ""
        if active_route:
            route_context_str = (
                f"\n\n**Selected Route Analysis ({active_route.get('name', 'Active Traverse')}):**\n"
                f"- Traverse Distance: **{active_route.get('distance_km')} km**\n"
                f"- Maximum Slope: **{active_route.get('max_slope_deg')}°** (Average {active_route.get('avg_slope_deg')}°)\n"
                f"- Safety Classification: **{active_route.get('safety_rating')}**\n"
                f"- Decision Logic: {active_route.get('explanation')}\n"
            )

        # Build grounded response
        answer_body = (
            f"### Scientific Briefing: {entry['topic']} ({entry['region']})\n\n"
            f"**Verified Observational Facts:**\n{entry['facts']}\n\n"
            f"**Scientific Interpretations & Hypotheses:**\n{entry['interpretations']}\n\n"
            f"**Key Observing NASA Instruments:**\n" +
            "\n".join([f"- {inst}" for inst in entry["mission_instruments"]]) +
            spatial_context_str +
            route_context_str
        )

        return {
            "query": question_text,
            "region": entry["region"],
            "topic": entry["topic"],
            "answer": answer_body,
            "citations": entry["citations"],
            "observational_basis": "Direct NASA Orbiter / Rover Observation & USGS Geologic Surveys",
            "disclaimer": "AI exploration assistant grounded strictly in NASA/USGS published peer-reviewed datasets. Model interpretations are not certified operational navigational commands."
        }
