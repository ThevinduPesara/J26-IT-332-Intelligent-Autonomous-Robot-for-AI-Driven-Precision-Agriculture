"""NutrientOS · world-class educational dashboard for chilli nutrient-dose research.

Run: streamlit run frontend/app.py --server.port 8501
Requires the FastAPI backend on API_URL.
"""
from __future__ import annotations

import io
import json
import os
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("NUTRIENTOS_API_URL", "http://127.0.0.1:8071").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://doa.gov.lk/field-crops-chilli-si/"

st.set_page_config(
    page_title="NutrientOS | Chilli Intelligence",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
:root {--mint:#3edba4;--ink:#e9f3ed;--sub:#98aaa5;--glass:#101e1e;}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{font-family:'DM Sans',sans-serif!important;}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 83% 3%, #1a4034 0%, transparent 34%),linear-gradient(155deg,#061313 0%,#0a1719 48%,#101a20 100%);color:#eaf4ee;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0b2421,#081714)!important;border-right:1px solid #27423a;}
[data-testid="stSidebar"] *{color:#dceee7;}
.block-container{padding-top:1.6rem;padding-bottom:4rem;max-width:1650px;}
h1,h2,h3,h4{font-family:'Outfit',sans-serif!important;letter-spacing:-.035em!important;}
h1{font-weight:800!important;}
[data-testid="stMetric"]{border:1px solid #2a4540;background:#102320;border-radius:17px;padding:17px 19px;}
[data-testid="stMetricLabel"]{color:#9cb7ad!important;}
[data-testid="stMetricValue"]{font-family:'Outfit';font-size:1.75rem!important;}
.stButton>button[kind="primary"]{background:#5ae1a8!important;color:#05211b!important;border:none!important;font-weight:800!important;border-radius:12px!important;}
.stButton>button{border-radius:12px!important;}
[data-baseweb="tab-list"]{background:rgba(255,255,255,.025);border-radius:11px;}
[data-baseweb="tab"]{font-weight:700!important;}
.stAlert{border-radius:14px;}
[data-testid="stFileUploader"]{border-radius:15px;}
.hero{padding:31px 36px;margin:5px 0 23px;border-radius:23px;background:radial-gradient(circle at 90% 12%,#4b9a72 0%,transparent 34%),linear-gradient(117deg,#143d33,#0b2a29 60%,#123831);border:1px solid #4a8a73;position:relative;overflow:hidden;}
.eyebrow{letter-spacing:.19em;text-transform:uppercase;font-weight:800;font-size:.73rem;color:#8df3c6;margin-bottom:13px;}
.hero h1{font-size:clamp(2.2rem,4.3vw,4rem);font-weight:800;line-height:1.0;color:#f2fff8;margin:0 0 11px;}
.hero p{font-size:1.08rem;color:#c1dace;max-width:830px;line-height:1.55;margin:0;}
.hero-foot{margin-top:23px;font-size:.76rem;color:#99dfbb;letter-spacing:.08em;font-weight:700;}
.panel{background:#112321;border:1px solid #2c4640;border-radius:18px;padding:21px 24px;margin:9px 0 19px;}
.panel-title{font-family:'Outfit';font-size:1.2rem;font-weight:700;margin-bottom:6px;color:#e8f7ef;}
.panel-sub{font-size:.87rem;color:#9ab5aa;line-height:1.6;}
.slabel{font-weight:800;color:#6de8b4;letter-spacing:.12em;text-transform:uppercase;font-size:.71rem;margin-top:12px;margin-bottom:7px;}
.muted{color:#9cafa8;font-size:.82rem;line-height:1.6;}
.brand{font-family:'Outfit';font-size:1.7rem;font-weight:800;color:#effff4;letter-spacing:-.05em;}
.brand small{font-family:'DM Sans';font-weight:700;letter-spacing:.12em;color:#68dbad;font-size:.65rem;display:block;}
.pill{display:inline-block;background:#184c3a;color:#b5fadc;font-size:.72rem;font-weight:800;border-radius:99px;padding:5px 11px;margin:4px 7px 4px 0;}
.pill.ghost{background:#28383b;color:#b5cacc;}
.badgewarn{background:#593a19;border:1px solid #8c6b3d;border-radius:13px;color:#ffdda5;padding:11px 16px;font-size:.89rem;line-height:1.5;}
.smallfoot{font-size:.78rem;color:#879e95;text-align:center;margin-top:20px;border-top:1px solid #243b35;padding-top:16px;}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)


def api_get(path: str) -> dict:
    response = requests.get(API_URL + path, timeout=6)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict) -> dict:
    response = requests.post(API_URL + path, json=payload, timeout=20)
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"API {response.status_code}: {detail}")
    return response.json()


def format_num(n, unit="", precision=3):
    if n is None:
        return "—"
    return f"{n:,.{precision}f}{' ' + unit if unit else ''}"


def graph_style(fig, height=310):
    fig.update_layout(
        height=height, autosize=True, margin=dict(l=7, r=9, t=18, b=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe9e2", family="DM Sans"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(gridcolor="#284139", zeroline=False),
        hoverlabel=dict(bgcolor="#132b25"),
    )
    return fig


with st.sidebar:
    st.markdown('<div class="brand">🌱 NutrientOS <small>MANJITHA · RESEARCH STUDIO</small></div>', unsafe_allow_html=True)
    st.caption("Chilli · Liquid NPK · Soil intelligence")
    st.divider()
    try:
        healthy = api_get("/health")
        st.success(f"● API online · v{healthy['version']}")
    except requests.RequestException:
        healthy = None
        st.error("● API offline — start FastAPI on port 8071")
    st.markdown('<div class="slabel">Project settings</div>', unsafe_allow_html=True)
    area = st.number_input("Cultivation area", min_value=0.01, max_value=100000.0, value=10.0, step=1.0)
    unit = st.selectbox("Unit", ["m2", "perch", "acre", "hectare"], format_func=lambda x: {"m2":"Square metres (m²)","perch":"Perches","acre":"Acres","hectare":"Hectares"}[x])
    plants = st.number_input("Number of chilli plants", min_value=1, max_value=1000000, value=20, step=1)
    stage_week = st.select_slider("DOA application stage", options=[0, 2, 4, 8, 12, 16], value=4, format_func=lambda v: "Basal" if v == 0 else f"Week {v}")
    use_date = st.checkbox("Track transplant date", value=False)
    transplant_date = st.date_input("Transplant date", value=date.today()) if use_date else None
    st.divider()
    st.markdown('<div class="slabel">Methodology</div>', unsafe_allow_html=True)
    mode = st.radio("Calculation mode", options=["reference", "experimental_soil"],
                    format_func=lambda x: "DOA reference" if x == "reference" else "Experimental soil budget",
                    help="Reference mode never uses demo sensors to change a dose. Soil mode requires explicit transfer coefficients.")
    if mode == "experimental_soil":
        st.warning("Research simulation only. Soil transfer coefficients must be externally validated.", icon="⚠️")
    st.divider()
    st.markdown('<div class="muted">This is a calculation prototype, not an autonomous fertilizer applicator.</div>', unsafe_allow_html=True)

st.markdown("""
<section class="hero">
  <div class="eyebrow">Precision Agriculture / Research Interface</div>
  <h1>Every drop, grounded<br>in better data.</h1>
  <p>Explore Sri Lanka's chilli fertilizer reference schedule, simulate soil NPK measurements, and compare a single liquid fertilizer against independently modelled nutrient targets.</p>
  <div class="hero-foot">🌿 FIELD CHILLI &nbsp; · &nbsp; 🧪 SOIL EXPERIMENTS &nbsp; · &nbsp; 💧 LIQUID NPK</div>
</section>
""", unsafe_allow_html=True)
st.markdown('<div class="badgewarn">⚠ Research demonstration only. Dummy sensors are not laboratory soil tests; calculated liquid volumes must not be applied to crops or transmitted to pumps without independent agronomic and product-label validation.</div>', unsafe_allow_html=True)

sensor_tab, composer_tab, research_tab = st.tabs(["🌱 Field & Soil", "💧 Liquid Formulation", "📈 Research & Reports"])

with sensor_tab:
    st.markdown("### Soil telemetry sandbox")
    st.caption("Input values are simulated, manually adjustable, and not connected to IoT devices yet.")
    col1, col2, col3 = st.columns(3)
    with col1:
        n = st.number_input("N — nitrogen (mg/kg)", min_value=0.0, max_value=100000.0, value=80.0, step=1.0)
    with col2:
        p = st.number_input("P — elemental phosphorus (mg/kg)", min_value=0.0, max_value=100000.0, value=12.0, step=1.0)
    with col3:
        k = st.number_input("K — elemental potassium (mg/kg)", min_value=0.0, max_value=100000.0, value=90.0, step=1.0)
    pH = st.number_input("Soil pH (display only)", min_value=0.0, max_value=14.0, value=6.3, step=0.1)
    data_soil = pd.DataFrame({"Nutrient":["N","P","K"],"Simulated sensor value (mg/kg)":[n,p,k]})
    fig = go.Figure(go.Bar(x=data_soil["Nutrient"], y=data_soil["Simulated sensor value (mg/kg)"],
                           marker=dict(color=["#55d3aa", "#89dba6", "#d5cc8c"], line=dict(width=0)),
                           text=data_soil["Simulated sensor value (mg/kg)"], textposition="outside"))
    fig.update_layout(yaxis_title="Sensor display only · mg/kg")
    st.plotly_chart(graph_style(fig, 290), use_container_width=True)
    st.info("Soil P/K lab methods, extractants and calibration affect what these mg/kg values mean. No direct mg/kg → crop-available kg/ha conversion is scientifically justified without calibration.")
    crop_photo = st.file_uploader("Optional chilli plant photo (for field record only)", type=["jpg", "jpeg", "png"])
    if crop_photo is not None:
        st.image(crop_photo, caption="Photo preview only — no image-based fertilizer prediction is performed.", width=350)

with composer_tab:
    st.markdown("### One-tank NPK liquid composer")
    st.caption("Enter the guaranteed analysis as N–P₂O₅–K₂O weight percentages, not elemental P/K. The example values are placeholders.")
    a, b, c = st.columns(3)
    with a:
        n_pct = st.number_input("Label N (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
    with b:
        p_pct = st.number_input("Label P₂O₅ (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
    with c:
        k_pct = st.number_input("Label K₂O (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
    d, e = st.columns(2)
    with d:
        density = st.number_input("Product density (g/mL)", min_value=0.01, max_value=3.0, value=1.10, step=0.01)
    with e:
        dilution = st.number_input("Total dilution factor", min_value=1.0, max_value=10000.0, value=1.0, step=1.0,
                                   help="1 = undiluted original product; 10 = diluted to ten times the starting stock volume. Assume correct mixing.")
    st.markdown('<div class="panel"><div class="panel-title">Composition is not interchangeable with DOA solid fertilizers</div><div class="panel-sub">Sri Lanka DOA specifies product masses of urea, TSP, and MOP. A ready-made one-tank NPK liquid delivers N, P₂O₅ and K₂O in one fixed ratio. The simulation compares that fixed ratio with the modelled targets; it does not approve a dose.</div></div>', unsafe_allow_html=True)

with research_tab:
    st.markdown("### Research calibration gate")
    st.caption("In the soil-budget mode, provide experimentally derived coefficients mapping the particular N/P/K sensor methods to crop-available nutrient equivalents (kg/ha per sensor mg/kg). They are *not* general constants.")
    use_coefficients = st.checkbox("I want to enter experimental coefficients for a simulation", value=False,
                                  help="Checking this enables a mathematical research preview only, not a fertilizer prescription.")
    if use_coefficients:
        x, y, z = st.columns(3)
        with x:
            n_coeff = st.number_input("N coefficient · kg/ha per mg/kg", min_value=0.0, max_value=100.0, value=0.20, step=0.01)
        with y:
            p_coeff = st.number_input("P₂O₅-equivalent coefficient", min_value=0.0, max_value=100.0, value=0.50, step=0.01)
        with z:
            k_coeff = st.number_input("K₂O-equivalent coefficient", min_value=0.0, max_value=100.0, value=0.35, step=0.01)
        provenance = st.text_input("Coefficient study/lab/source", value="ILLUSTRATIVE VALUES ONLY — not validated for local soil")
        st.warning("Shown coefficients are synthetic placeholders, not taken from the cited studies. Do not dispense from these values.")
    else:
        n_coeff = p_coeff = k_coeff = None
        provenance = ""
        st.info("Without explicit coefficients, the application correctly refuses to calculate a soil-adjusted liquid volume.")
    st.markdown("""
<div class="panel">
 <div class="panel-title">Why the science is separated</div>
 <div class="panel-sub">DOA baseline = a published standard schedule. Experimental soil budget = a research exercise with user-supplied coefficients. It is not a trained AI model and is not an STCR equation validated for Sri Lanka. A production recommendation requires actual local experimental data and independent verification.</div>
</div>
""", unsafe_allow_html=True)

payload = {
    "plot": {"area": area, "unit": unit, "plants": int(plants), "stage_week": int(stage_week),
             "transplant_date": transplant_date.isoformat() if transplant_date else None},
    "soil": {"n_mgkg": n, "p_mgkg": p, "k_mgkg": k, "ph": pH, "origin": "SIMULATED"},
    "liquid": {"label_n_percent": n_pct, "label_p2o5_percent": p_pct, "label_k2o_percent": k_pct,
               "density_g_ml": density, "dilution_factor": dilution},
    "calculation_mode": mode,
    "calibration": {"n_kg_ha_per_mgkg": n_coeff, "p2o5_kg_ha_per_mgkg": p_coeff,
                    "k2o_kg_ha_per_mgkg": k_coeff, "provenance": provenance},
}

st.divider()
run = st.button("Calculate & analyze", type="primary", use_container_width=True, disabled=healthy is None)

if run:
    try:
        st.session_state["result"] = api_post("/api/v1/calculate", payload)
        st.session_state["last_payload"] = payload
    except (requests.RequestException, RuntimeError) as exc:
        st.error(f"Calculation failed: {exc}")

if "result" not in st.session_state:
    st.markdown('<div class="panel"><div class="panel-title">Your research workspace is ready</div><div class="panel-sub">Enter plot dimensions, explore dummy readings and the liquid formulation, then click Calculate & analyze. The DOA reference report is available even without soil-calibration coefficients.</div></div>', unsafe_allow_html=True)
else:
    result = st.session_state["result"]
    stage_target = result["reference"]["stage_nutrient_g_plot"]
    stage_reference_products = result["reference"]["stage_product_g_plot"]
    result_mode = result["mode"]
    results_tab, schedule_tab, audit_tab = st.tabs(["✨ Results overview", "📅 Application schedule", "🔎 Audit & export"])

    with results_tab:
        st.markdown("### Current analysis")
        st.caption(f"Stage: week {result['plot']['stage_week']} · area: {format_num(result['plot']['area_m2'], 'm²', 2)} · status: {result['status']}")
        a, b, c, d = st.columns(4)
        a.metric("Reference Urea · stage", format_num(stage_reference_products["urea"], "g", 2))
        b.metric("Reference TSP · stage", format_num(stage_reference_products["tsp"], "g", 2))
        c.metric("Reference MOP · stage", format_num(stage_reference_products["mop"], "g", 2))
        modelled = result["modelled"]
        comparison = modelled["liquid_comparison"]
        if comparison is None:
            d.metric("Liquid volume", "Not calculated")
            if result_mode == "reference":
                st.info("Reference mode displays DOA solid product masses only. To experiment with a liquid volume, select Experimental soil budget and explicitly enter coefficients.")
            else:
                st.warning("Experimental mode requires all three nutrient transfer coefficients. Open Research & Reports and enable experimental coefficients.")
        else:
            d.metric("Research liquid fit", format_num(comparison["comparison_volume_ml"], "mL", 2))
            st.warning("The displayed liquid volume is an **unvalidated mathematical fit**, not a safe or approved application rate. Pumps stay disabled.")
            st.markdown("#### Experimental nutrient balance · current stage")
            requirement = modelled["stage_target_nutrient_g_plot"]
            supplied = comparison["nutrients_delivered_g"]
            fig2 = go.Figure()
            fig2.add_bar(name="Illustrative target", x=list(requirement), y=list(requirement.values()), marker_color="#5ad5a6")
            fig2.add_bar(name="Single-liquid delivery", x=list(supplied), y=list(supplied.values()), marker_color="#d2ae67")
            fig2.update_layout(barmode="group", yaxis_title="Grams per plot")
            st.plotly_chart(graph_style(fig2, 320), use_container_width=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("N target", format_num(requirement["N"], "g"))
            c2.metric("P₂O₅ target", format_num(requirement["P2O5"], "g"))
            c3.metric("K₂O target", format_num(requirement["K2O"], "g"))
            st.markdown("#### Fixed-ratio compatibility")
            for warning in comparison["constraints"]:
                st.caption("⚠ " + warning)
            st.markdown('<div class="badgewarn">Hardware output is intentionally locked: pump_target_ml = null, pump_enabled = false.</div>', unsafe_allow_html=True)

        st.markdown("#### DOA nutrient-equivalent reference · this stage")
        nut_table = pd.DataFrame({"Nutrient":["N", "P₂O₅", "K₂O"],
                                  "Reference fertilizer nutrient input (g / plot)":list(stage_target.values())})
        st.dataframe(nut_table, hide_index=True, use_container_width=True)

    with schedule_tab:
        st.markdown("### Sri Lanka field chilli · DOA schedule")
        schedule_rows = []
        for line in result["reference"]["schedule"]:
            schedule_rows.append({"Stage":line["stage"], "Week":line["week"],
                                  "Date": line["due_date"] or "Not set",
                                  "Urea · g":line["reference_products_g_for_plot"]["urea"],
                                  "TSP · g":line["reference_products_g_for_plot"]["tsp"],
                                  "MOP · g":line["reference_products_g_for_plot"]["mop"]})
        df_schedule = pd.DataFrame(schedule_rows)
        st.dataframe(df_schedule, hide_index=True, use_container_width=True)
        fig3 = go.Figure()
        for fert, color in (("Urea", "#52d2a4"),("TSP", "#deb773"),("MOP", "#8aafdb")):
            fig3.add_bar(x=df_schedule["Week"].astype(str), y=df_schedule[f"{fert} · g"], name=fert, marker_color=color)
        fig3.update_layout(barmode="stack", xaxis_title="Week after transplanting", yaxis_title="Fertilizer product mass (g per plot)")
        st.plotly_chart(graph_style(fig3, 325), use_container_width=True)
        st.info("These are DOA-referenced Urea/TSP/MOP **product masses**. They are not the same as total plant nutrient demand, and not a liquid fertilizer application schedule.")
        st.download_button("Download DOA schedule CSV", df_schedule.to_csv(index=False).encode("utf-8"), file_name="chilli_doa_reference_schedule.csv", mime="text/csv")

    with audit_tab:
        st.markdown("### Transparent calculations & research traceability")
        st.caption("Every run can be exported and audited. Values are stored in local browser session only; no database or sensors are connected.")
        st.download_button("Download complete result JSON", data=json.dumps(result, indent=2).encode("utf-8"), file_name="nutrientos_result.json", mime="application/json")
        st.download_button("Download input configuration JSON", data=json.dumps(st.session_state["last_payload"], indent=2).encode("utf-8"), file_name="nutrientos_input.json", mime="application/json")
        with st.expander("View the full API output"):
            st.json(result)
        st.markdown("#### Source and experimental boundaries")
        st.markdown(f"- [Sri Lanka DOA field chilli fertilizer recommendation]({SOURCE_URL})")
        st.markdown("- [Maragani et al. (2023): Chilli targeted-yield soil test research](https://doi.org/10.18805/ag.D-5782)")
        st.markdown("- NPK labels generally express N–P₂O₅–K₂O; soil sensing often expresses elemental N/P/K (mg/kg). The current sensor readings only influence the experimental mode through user-entered transfer coefficients.")
        st.markdown("- Liquid preview solves a one-variable **nonnegative least-squares** nutrient-ratio fit. It is not an AI-trained model; it is not a farm-use recommendation.")
        st.markdown("- Real crop dosing would require local agronomic calibration, correct fertilizer analysis and density, compatibility/mixing checks, water volume, repeated field validation, and human approval.")

st.markdown('<div class="smallfoot">NutrientOS Research Studio · Built for Manjitha’s chilli NPK module · Educational planning / no automatic dispensing · Source: Sri Lanka DOA</div>', unsafe_allow_html=True)
