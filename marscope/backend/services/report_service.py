"""
MARSCOPE Mission Dossier & Report Generation Service
Generates structured JSON mission exports and professional PDF dossiers via ReportLab.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import ATTRIBUTION_STATEMENT, MAP_LAYERS

class ReportService:
    @classmethod
    def generate_json_dossier(cls, route_data, eva_budget, mission_meta=None):
        """
        Builds a comprehensive, self-contained JSON mission dossier.
        """
        meta = mission_meta or {}
        now_iso = datetime.utcnow().isoformat() + "Z"

        return {
            "dossier_version": "2.0.0",
            "generation_timestamp": now_iso,
            "mission": {
                "name": meta.get("mission_name", "MARSCOPE-EVA-ALPHA"),
                "crew_commander": meta.get("commander", "Commander Jane Doe"),
                "crew_size": meta.get("crew_size", 2),
                "objective": meta.get("objective", "Scientific Reconnaissance & In-Situ Sampling"),
                "target_region": meta.get("target_region", "Jezero Crater / Nili Planum")
            },
            "route_plan": route_data,
            "life_support_budget": eva_budget,
            "dataset_provenance": MAP_LAYERS,
            "legal_and_scientific_disclaimer": ATTRIBUTION_STATEMENT
        }

    @classmethod
    def generate_pdf_dossier(cls, route_data, eva_budget, mission_meta=None):
        """
        Generates a professional multi-page PDF mission dossier byte stream.
        """
        meta = mission_meta or {}
        pdf_buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom planetary design color palette
        c_primary = colors.HexColor("#C1440E")     # Mars rust
        c_dark = colors.HexColor("#1A1817")        # Charcoal
        c_accent = colors.HexColor("#0288D1")      # Deep Cyan
        c_sand = colors.HexColor("#E8D5B5")        # Regolith Sand
        c_light = colors.HexColor("#F5F3EF")       # Clean Off-white
        c_danger = colors.HexColor("#D32F2F")      # Alert Red
        c_safe = colors.HexColor("#2E7D32")        # Safe Green

        title_style = ParagraphStyle(
            'MarsTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=c_primary,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'MarsSub',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#555555"),
            spaceAfter=12
        )
        section_style = ParagraphStyle(
            'MarsSection',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=c_primary,
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'MarsBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=c_dark
        )
        callout_style = ParagraphStyle(
            'MarsCallout',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=c_dark
        )
        caption_style = ParagraphStyle(
            'MarsCaption',
            parent=styles['Normal'],
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#777777")
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("MARSCOPE // MISSION EXPLORATION DOSSIER", title_style))
        elements.append(Paragraph(
            f"<b>Planetary Exploration & Survival Plan</b> | NASA Space Apps Challenge 2026<br/>"
            f"Target Region: <b>{meta.get('target_region', 'Martian Surface')}</b> | Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            subtitle_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceAfter=12))

        # 2. Mission Overview Table
        mission_table_data = [
            [
                Paragraph("<b>Mission Designation:</b>", body_style),
                Paragraph(meta.get("mission_name", "MARSCOPE-EVA-01"), body_style),
                Paragraph("<b>Traverse Strategy:</b>", body_style),
                Paragraph(route_data.get("name", "Optimized Traverse"), body_style)
            ],
            [
                Paragraph("<b>Crew Size:</b>", body_style),
                Paragraph(f"{meta.get('crew_size', 2)} Astronauts (Suited)", body_style),
                Paragraph("<b>Safety Rating:</b>", body_style),
                Paragraph(f"<font color='{c_safe if route_data.get('safety_rating') == 'SAFE' else c_danger}'><b>{route_data.get('safety_rating', 'CAUTION')}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Start Waypoint:</b>", body_style),
                Paragraph(f"{route_data.get('points', [[0,0]])[0][0]:.3f}°, {route_data.get('points', [[0,0]])[0][1]:.3f}°", body_style),
                Paragraph("<b>Destination:</b>", body_style),
                Paragraph(f"{route_data.get('points', [[0,0]])[-1][0]:.3f}°, {route_data.get('points', [[0,0]])[-1][1]:.3f}°", body_style)
            ],
            [
                Paragraph("<b>Total Distance:</b>", body_style),
                Paragraph(f"<b>{route_data.get('distance_km')} km</b>", body_style),
                Paragraph("<b>Estimated EVA Duration:</b>", body_style),
                Paragraph(f"<b>{eva_budget.get('total_eva_hours')} hours</b>", body_style)
            ]
        ]
        t_overview = Table(mission_table_data, colWidths=[110, 150, 110, 150])
        t_overview.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_light),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CCCCCC")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_overview)
        elements.append(Spacer(1, 10))

        # 3. Terrain & Topographic Profile
        elements.append(Paragraph("1. TOPOGRAPHIC & TERRAIN SAFETY PROFILE", section_style))
        terrain_data = [
            [
                Paragraph("<b>Start Elevation:</b>", body_style),
                Paragraph(f"{route_data.get('elev_start_m')} m", body_style),
                Paragraph("<b>End Elevation:</b>", body_style),
                Paragraph(f"{route_data.get('elev_end_m')} m", body_style),
            ],
            [
                Paragraph("<b>Elevation Range:</b>", body_style),
                Paragraph(f"[{route_data.get('elev_min_m')} m to {route_data.get('elev_max_m')} m]", body_style),
                Paragraph("<b>Total Ascent / Descent:</b>", body_style),
                Paragraph(f"+{route_data.get('elev_gain_m')} m / -{route_data.get('elev_loss_m')} m", body_style),
            ],
            [
                Paragraph("<b>Maximum Slope:</b>", body_style),
                Paragraph(f"<b>{route_data.get('max_slope_deg')}°</b>", body_style),
                Paragraph("<b>Average Gradient:</b>", body_style),
                Paragraph(f"{route_data.get('avg_slope_deg')}°", body_style),
            ]
        ]
        t_terrain = Table(terrain_data, colWidths=[110, 150, 110, 150])
        t_terrain.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EEEEEE")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(t_terrain)
        elements.append(Spacer(1, 6))

        # Route Explainability Box
        elements.append(Paragraph(
            f"<b>Navigation Decision Rationale:</b> {route_data.get('explanation')}",
            callout_style
        ))
        elements.append(Spacer(1, 10))

        # 4. Life Support & Return-to-Base (RTB) Feasibility
        elements.append(Paragraph("2. LIFE SUPPORT & RETURN-TO-BASE FEASIBILITY", section_style))
        o2 = eva_budget.get("o2", {})
        batt = eva_budget.get("battery", {})
        water = eva_budget.get("cooling_water", {})
        mass_grav = eva_budget.get("mass_and_gravity", {})

        rtb_status = eva_budget.get("feasibility_status", "NOMINAL_FEASIBLE")
        rtb_color = c_safe if eva_budget.get("is_rtb_feasible") else c_danger

        eva_table_data = [
            [
                Paragraph("<b>Subsystem</b>", body_style),
                Paragraph("<b>Consumed</b>", body_style),
                Paragraph("<b>Capacity</b>", body_style),
                Paragraph("<b>Remaining Margin</b>", body_style),
                Paragraph("<b>Safety Status</b>", body_style)
            ],
            [
                Paragraph("<b>Oxygen (O2)</b>", body_style),
                Paragraph(f"{o2.get('consumed_per_astronaut_l')} L", body_style),
                Paragraph(f"{o2.get('capacity_l')} L", body_style),
                Paragraph(f"<b>{o2.get('remaining_pct')}%</b>", body_style),
                Paragraph("NOMINAL" if o2.get('remaining_pct', 0) >= 25 else "CRITICAL LOW", body_style)
            ],
            [
                Paragraph("<b>Suit Battery</b>", body_style),
                Paragraph(f"{batt.get('consumed_wh')} Wh", body_style),
                Paragraph(f"{batt.get('capacity_wh')} Wh", body_style),
                Paragraph(f"<b>{batt.get('remaining_pct')}%</b>", body_style),
                Paragraph("NOMINAL" if batt.get('remaining_pct', 0) >= 25 else "CRITICAL LOW", body_style)
            ],
            [
                Paragraph("<b>Cooling Water</b>", body_style),
                Paragraph(f"{water.get('consumed_kg')} kg", body_style),
                Paragraph(f"{water.get('capacity_kg')} kg", body_style),
                Paragraph(f"<b>{water.get('remaining_pct')}%</b>", body_style),
                Paragraph("NOMINAL" if water.get('remaining_pct', 0) >= 25 else "CRITICAL LOW", body_style)
            ],
            [
                Paragraph("<b>Mars Weight</b>", body_style),
                Paragraph(f"Gravity: 3.72 m/s²", body_style),
                Paragraph(f"Cargo: {mass_grav.get('cargo_mars_weight_kg_equiv')} kg-eq", body_style),
                Paragraph(f"Astronaut: {mass_grav.get('astronaut_effective_weight_mars_kg')} kg-eq", body_style),
                Paragraph("0.38 Earth g", body_style)
            ]
        ]
        t_eva = Table(eva_table_data, colWidths=[90, 100, 100, 110, 120])
        t_eva.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_light),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CCCCCC")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_eva)
        elements.append(Spacer(1, 6))

        elements.append(Paragraph(
            f"<b>RTB Assessment:</b> <font color='{rtb_color}'><b>{rtb_status}</b></font> - {eva_budget.get('recommendation')}",
            body_style
        ))
        if eva_budget.get("warnings"):
            for w in eva_budget["warnings"]:
                elements.append(Paragraph(f"<font color='{c_danger}'>• WARNING: {w}</font>", body_style))
        elements.append(Spacer(1, 10))

        # 5. Scientific Exploration Stops
        elements.append(Paragraph("3. SCIENTIFIC TARGETS & IN-SITU INVESTIGATION STOPS", section_style))
        pois = route_data.get("pois", [])
        if pois:
            poi_rows = [
                [
                    Paragraph("<b>Target Site</b>", body_style),
                    Paragraph("<b>Type / Mineralogy</b>", body_style),
                    Paragraph("<b>NASA Instrument</b>", body_style),
                    Paragraph("<b>Detour</b>", body_style),
                    Paragraph("<b>Investigation Duration</b>", body_style)
                ]
            ]
            for p in pois[:4]:
                poi_rows.append([
                    Paragraph(f"<b>{p.get('name')}</b>", body_style),
                    Paragraph(p.get("type", "Geology"), body_style),
                    Paragraph(p.get("instrument", "Orbiter"), body_style),
                    Paragraph(f"{p.get('distance_from_route_km', 0)} km", body_style),
                    Paragraph(f"{p.get('est_duration_minutes', 60)} min", body_style)
                ])
            t_pois = Table(poi_rows, colWidths=[130, 120, 110, 60, 100])
            t_pois.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), c_light),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CCCCCC")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(t_pois)
        else:
            elements.append(Paragraph("No designated major scientific landmarks within the 50 km route buffer.", body_style))
        elements.append(Spacer(1, 10))

        # 6. Mapped Hazard Zones
        elements.append(Paragraph("4. MAPPED HAZARD ASSESSMENTS", section_style))
        hazards = route_data.get("hazards", [])
        if hazards:
            haz_rows = [
                [
                    Paragraph("<b>Hazard Zone</b>", body_style),
                    Paragraph("<b>Classification</b>", body_style),
                    Paragraph("<b>Severity</b>", body_style),
                    Paragraph("<b>Source Dataset</b>", body_style)
                ]
            ]
            for h in hazards[:4]:
                sev = h.get("severity", 1)
                haz_rows.append([
                    Paragraph(f"<b>{h.get('name')}</b>", body_style),
                    Paragraph(h.get("type", "Hazard"), body_style),
                    Paragraph(f"Level {sev}/3", body_style),
                    Paragraph(h.get("source_dataset", "NASA"), body_style)
                ])
            t_haz = Table(haz_rows, colWidths=[150, 140, 70, 160])
            t_haz.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), c_light),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CCCCCC")),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ]))
            elements.append(t_haz)
        else:
            elements.append(Paragraph("No critical mapped volcanic, canyon scarp, or boulder hazards encountered along this traverse corridor.", body_style))
        elements.append(Spacer(1, 14))

        # 7. Dataset Provenance & Legal Disclaimer
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CCCCCC"), spaceAfter=8))
        elements.append(Paragraph(
            "<b>Data Provenance & Traceability:</b> Base imagery from NASA Viking MDIM 2.1 (232m). Topography from Mars Global Surveyor MOLA MEGDR (463m). "
            "Thermal inertia from 2001 Mars Odyssey THEMIS IR (100m). Geological classifications from USGS Astrogeology Planetary Maps. "
            "Rover reference sites from NASA/JPL-Caltech Mars 2020 and MSL.",
            caption_style
        ))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(ATTRIBUTION_STATEMENT, caption_style))

        # Build document
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
