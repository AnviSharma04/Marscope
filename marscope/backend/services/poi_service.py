"""
MARSCOPE Science Points of Interest & Multi-Mission Exploration Targets
Grounded in published NASA rover, orbiter, and USGS planetary geologic datasets.
"""

from services.elevation_service import haversine_distance_km

SCIENCE_CATALOG = [
    {
        "id": "SCI-001",
        "name": "Jezero Western Fan Delta (Kodiak Outcrop)",
        "lat": 18.444,
        "lon": 77.452,
        "region": "Jezero Crater / Nili Planum",
        "type": "Ancient River Delta / Lacustrine Sediments",
        "mission": "Mars 2020 / MRO",
        "instrument": "Perseverance Mastcam-Z / SuperCam / MRO CRISM",
        "elevation_m": -2450,
        "geological_significance": "Distinct bottomset, foreset, and topset layered stratigraphy proving a sustained ancient standing lake fed by Neretva Vallis.",
        "supporting_observations": "CRISM infrared spectra show strong 2.2-µm and 1.9-µm absorption indicative of Fe/Mg smectite clays and carbonates.",
        "scientific_objective": "Search for potential biosignatures and collect intact core samples of fine lacustrine mudstone.",
        "recommended_investigation": "Microscopic Raman spectroscopy, deep UV fluorescence imaging, and rotary-percussive sample core drilling.",
        "est_duration_minutes": 90,
        "required_equipment": ["Portable Raman Spectrometer", "Microscopic Hand Lens Imager", "Core Sample Drill Kit", "Hermetic Sample Seal Tubes"],
        "science_value_score": 98,
        "source_url": "https://mars.nasa.gov/mars2020/mission/science/landing-site/"
    },
    {
        "id": "SCI-002",
        "name": "Jezero Séítah Olivine-Carbonate Outcrops",
        "lat": 18.388,
        "lon": 77.412,
        "region": "Jezero Crater",
        "type": "Igneous Bedrock & Carbonate Alteration",
        "mission": "Mars 2020",
        "instrument": "Perseverance PIXL / SHERLOC / SuperCam",
        "elevation_m": -2530,
        "geological_significance": "Cumulate igneous basement rock rich in coarse olivine grains altered by early Martian carbonated waters.",
        "supporting_observations": "PIXL X-ray fluorescence confirms high magnesium and iron content with crystalline carbonate rims.",
        "scientific_objective": "Determine crystallization age of igneous crust and early atmospheric CO2 drawdown history.",
        "recommended_investigation": "X-ray fluorescence elemental mapping, surface abrading tool inspection, regolith grain sizing.",
        "est_duration_minutes": 75,
        "required_equipment": ["X-Ray Fluorescence Scanner", "Surface Abrading Tool", "Polarized Petrographic Magnifier"],
        "science_value_score": 92,
        "source_url": "https://mars.nasa.gov/mars2020/multimedia/raw-images/"
    },
    {
        "id": "SCI-003",
        "name": "Gale Crater - Mount Sharp Hematite Ridge (Vera Rubin)",
        "lat": -4.680,
        "lon": 137.420,
        "region": "Gale Crater / Aeolis Palus",
        "type": "Sedimentary Ridge / Iron Oxide Mineralization",
        "mission": "Mars Science Laboratory (MSL)",
        "instrument": "Curiosity ChemCam / CheMin / APXS / MRO CRISM",
        "elevation_m": -4150,
        "geological_significance": "Narrow ridge elevated ~65 m above surrounding plains displaying intense crystalline gray hematite deposits.",
        "supporting_observations": "CheMin X-ray diffraction confirms stoichiometric hematite precipitated from dynamic groundwater redox fronts.",
        "scientific_objective": "Test geochemical conditions (pH, redox) of ancient groundwater percolation during Gale's drying phase.",
        "recommended_investigation": "Drill powder mineralogy extraction, alpha particle X-ray spectrometry on fresh cross-sections.",
        "est_duration_minutes": 80,
        "required_equipment": ["Mineralogical XRD/XRF Analyzer", "Rock Hammer & Chisel", "Spectroscopic Contact Sensor"],
        "science_value_score": 94,
        "source_url": "https://science.nasa.gov/mission/msl-curiosity/"
    },
    {
        "id": "SCI-004",
        "name": "Gale Crater - Clay-Bearing Unit (Glen Torridon)",
        "lat": -4.750,
        "lon": 137.450,
        "region": "Gale Crater",
        "type": "Phyllosilicate Bedrock Trough",
        "mission": "Mars Science Laboratory (MSL)",
        "instrument": "Curiosity SAM / CheMin / MRO CRISM",
        "elevation_m": -4020,
        "geological_significance": "Exposed layered mudstones rich in potassium- and iron-bearing smectite clay minerals formed in neutral pH water.",
        "supporting_observations": "CRISM 1.9-µm and 2.29-µm vibrational overtone signatures; SAM gas chromatograph detected diverse organic compounds.",
        "scientific_objective": "Analyze preservation potential of prebiotic organic molecules encapsulated within clay interlayers.",
        "recommended_investigation": "Pyrolysis mass spectrometry sample digestion, organic carbon quantification.",
        "est_duration_minutes": 100,
        "required_equipment": ["Miniature Pyrolysis Gas Chromatograph", "Contamination-Free Sampling Spatula", "Cryogenic Storage Decks"],
        "science_value_score": 96,
        "source_url": "https://science.nasa.gov/resource/curiositys-proposed-path-up-mount-sharp/"
    },
    {
        "id": "SCI-005",
        "name": "Valles Marineris - Candor Chasma Layered Deposits",
        "lat": -6.500,
        "lon": -75.700,
        "region": "Valles Marineris",
        "type": "Interior Layered Deposits (ILD) / Hydrated Sulfates",
        "mission": "MRO / Mars Express",
        "instrument": "MRO CRISM / HiRISE / MEX OMEGA",
        "elevation_m": -6800,
        "geological_significance": "Gigantic kilometer-thick stacks of rhythmic sulfate-bearing sediment beds, potentially deposited by sub-ice volcanism or playa lakes.",
        "supporting_observations": "CRISM spectra identify polyhydrated sulfates (kieserite, epsomite, gypsum) with high spatial continuity.",
        "scientific_objective": "Decipher Amazonian-Hesperian transition climate oscillation records and sulfur cycle.",
        "recommended_investigation": "High-resolution stratigraphic photo-documentation, localized laser-induced breakdown spectroscopy.",
        "est_duration_minutes": 120,
        "required_equipment": ["Long-Range LIBS Laser Spectrometer", "Stereo Telephoto Gigapixel Rig", "Geological Compass & Inclinometer"],
        "science_value_score": 95,
        "source_url": "https://trek.nasa.gov/mars/"
    },
    {
        "id": "SCI-006",
        "name": "Olympus Mons - Aureole Basal Glacial Moraine",
        "lat": 19.500,
        "lon": -135.200,
        "region": "Tharsis Montes",
        "type": "Basal Glacier Lobes / Volcanic-Ice Interactions",
        "mission": "MGS / MRO",
        "instrument": "MGS MOLA / MRO CTX / HiRISE",
        "elevation_m": 850,
        "geological_significance": "Concentric ridges and lobate debris aprons indicating former tropical mountain glaciation on the volcano flanks.",
        "supporting_observations": "SHARAD radar sounding shows low-attenuation dielectric reflections consistent with buried debris-covered water ice.",
        "scientific_objective": "Verify presence of accessible buried glacial water-ice deposits for in-situ resource utilization (ISRU).",
        "recommended_investigation": "Ground-penetrating radar profiling, shallow thermal probe depth insertion.",
        "est_duration_minutes": 110,
        "required_equipment": ["Subsurface Ground-Penetrating Radar (GPR)", "Thermal Conductivity Depth Needle", "Ice Core Borer"],
        "science_value_score": 97,
        "source_url": "https://trek.nasa.gov/mars/"
    },
    {
        "id": "SCI-007",
        "name": "Mawrth Vallis - Ancient Phyllosilicate Sequence",
        "lat": 23.990,
        "lon": -18.960,
        "region": "Oxia Palus / Arabia Terra",
        "type": "Exposed Ancient Stratigraphy / Multiple Clay Horizons",
        "mission": "MRO / Mars Express",
        "instrument": "CRISM / OMEGA / HiRISE",
        "elevation_m": -2240,
        "geological_significance": "Over 200 meters of vertically stratified Noachian clays showing transition from nontronite (Fe/Mg) to montmorillonite/kaolinite (Al-rich).",
        "supporting_observations": "One of the most extensive and diverse hydrated silicate signatures detected on Mars.",
        "scientific_objective": "Study the geochemical evolution of early Mars water chemistry from deep weathering to leaching.",
        "recommended_investigation": "Reflectance spectroscopy transect, stratigraphic column logging, sample extraction.",
        "est_duration_minutes": 90,
        "required_equipment": ["VNIR Contact Spectrometer", "Hand-Held Geological Core Drill", "High-Precision GPS/Inclinometer"],
        "science_value_score": 95,
        "source_url": "https://astrogeology-usgs.hub.arcgis.com/pages/interactive-maps-mars"
    },
    {
        "id": "SCI-008",
        "name": "Arcadia Planitia - Subsurface Sheet Ice (SWIM)",
        "lat": 39.200,
        "lon": -171.000,
        "region": "Arcadia Planitia",
        "type": "Subsurface Excess Water Ice / Terraced Craters",
        "mission": "MRO / Mars Odyssey / Subsurface Water Ice Mapping (SWIM)",
        "instrument": "MRO SHARAD / Odyssey GRS / HiRISE",
        "elevation_m": -3800,
        "geological_significance": "Widespread shallow water-ice sheet situated 1 to 5 meters below dry regolith overburden, accessible for human base ISRU.",
        "supporting_observations": "SHARAD radar dielectric constant epsilon ~ 3.1; Odyssey Gamma Ray Spectrometer shows hydrogen enrichment (> 10% water equiv).",
        "scientific_objective": "Map ice purity, thickness, and extractability for astronaut drinking water and propellant synthesis.",
        "recommended_investigation": "Active shallow seismic sounding, automated Auger drilling down to 2.5 meters.",
        "est_duration_minutes": 120,
        "required_equipment": ["Lightweight Rotary Percussive Auger", "Downhole Neutron Probe", "Water Purification Test Cell"],
        "science_value_score": 99,
        "source_url": "https://swim.psi.edu/"
    },
    {
        "id": "SCI-009",
        "name": "Meridiani Planum - Hematite Concretions ('Blueberries')",
        "lat": -1.946,
        "lon": -5.530,
        "region": "Meridiani Planum",
        "type": "Evaporite Sulfates & Hematite Spherules",
        "mission": "Mars Exploration Rover (MER-B)",
        "instrument": "Opportunity Mössbauer / APXS / Microscopic Imager",
        "elevation_m": -1420,
        "geological_significance": "Dispersed 1-4 mm gray hematite concretions formed within acidic, sulfate-saturated groundwater percolation.",
        "supporting_observations": "Mössbauer spectra reveal ferric iron Fe3+ in jarosite and crystalline hematite.",
        "scientific_objective": "Quantify ancient groundwater evaporation timescales and fluid acidity.",
        "recommended_investigation": "Micro-imaging of sphere internal concentric structures, chemical assay.",
        "est_duration_minutes": 60,
        "required_equipment": ["Microscopic Imager", "Mossbauer Contact Sensor", "Sample Sieve & Vials"],
        "science_value_score": 88,
        "source_url": "https://mars.nasa.gov/mer/mission/overview/"
    },
    {
        "id": "SCI-010",
        "name": "Elysium Planitia - Cerberus Fossae Young Lava Flows",
        "lat": 4.500,
        "lon": 135.620,
        "region": "Elysium Planitia (InSight Site)",
        "type": "Recent Basaltic Plains / Marsquake Epicenters",
        "mission": "InSight Lander / MRO",
        "instrument": "InSight SEIS / MRO HiRISE",
        "elevation_m": -2610,
        "geological_significance": "Among the youngest volcanic lava and tectonic fissure surfaces on Mars (< 10-50 Ma); epicenters of active low-frequency marsquakes.",
        "supporting_observations": "HiRISE boulders displaced by seismic shaking; SEIS detected over 1,300 marsquakes originating from Cerberus Fossae.",
        "scientific_objective": "Characterize contemporary Martian tectonic and volcanic seismicity and mantle plume dynamics.",
        "recommended_investigation": "Deploy short-period nodal seismometer array, measure regolith seismic velocity.",
        "est_duration_minutes": 90,
        "required_equipment": ["Portable 3-Component Seismometer", "Regolith P-Wave Hammer", "Laser Distance Meter"],
        "science_value_score": 91,
        "source_url": "https://mars.nasa.gov/insight/"
    }
]

class PoiService:
    @classmethod
    def get_all_pois(cls):
        return SCIENCE_CATALOG

    @classmethod
    def get_poi_by_id(cls, poi_id):
        for p in SCIENCE_CATALOG:
            if p["id"] == poi_id:
                return p
        return None

    @classmethod
    def find_nearest_poi(cls, lat, lon):
        best_p = None
        min_d = float('inf')
        for p in SCIENCE_CATALOG:
            d = haversine_distance_km(lat, lon, p["lat"], p["lon"])
            if d < min_d:
                min_d = d
                best_p = p
        return best_p, round(min_d, 1)

    @classmethod
    def pois_near_route(cls, route_points, threshold_km=100.0):
        """
        Finds all scientific targets within threshold_km of any point on the route.
        Returns targets sorted by proximity and scientific value score.
        """
        matched = {}
        for p in SCIENCE_CATALOG:
            p_lat, p_lon = p["lat"], p["lon"]
            closest_d = min(haversine_distance_km(pt[0], pt[1], p_lat, p_lon) for pt in route_points)
            if closest_d <= threshold_km:
                item = dict(p)
                item["distance_from_route_km"] = round(closest_d, 1)
                matched[p["id"]] = item

        # Sort by distance
        res = list(matched.values())
        res.sort(key=lambda x: x["distance_from_route_km"])
        return res
