# NutrientOS — Manjitha's Liquid NPK Research Studio

A complete local **FastAPI backend + Streamlit frontend** for the **AI and IoT-Based NPK Fertilizer Recommendation for Chilli Plants** research module. Designed for dummy sensors today and future live-sensor integration. This prototype does **not** claim a trained AI model, calibrated soil prediction, or operational fertilizer prescription.

> **RESEARCH / SIMULATION ONLY. DO NOT USE THE VOLUMES FOR REAL FERTILIZER APPLICATION OR PUMP CONTROL.** Real fertilizer dosing requires independently validated Sri Lankan chilli/soil-response coefficients, lab-calibrated NPK sensor signals, known fertilizer analysis and density, agronomist approval and dispensing safety tests.

## Quick start — Windows / Anaconda Prompt

1. Extract `Manjitha_NPK_Dose_Studio_Complete.zip` to:
   `C:\Users\LENOVO\Downloads\Manjitha_NPK_Dose_Studio`

2. Open **Anaconda Prompt** (or a properly configured conda terminal). Create a **separate environment** so installation does not modify your `torch_gpu` training environment:

```bat
conda create -n npk_ui python=3.10 -y
conda activate npk_ui
cd /d "C:\Users\LENOVO\Downloads\Manjitha_NPK_Dose_Studio"
python -m pip install -r requirements.txt
```

3. Run both services in two different Anaconda Prompt windows:

**Terminal A — FastAPI**

```bat
conda activate npk_ui
cd /d "C:\Users\LENOVO\Downloads\Manjitha_NPK_Dose_Studio"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8071
```

**Terminal B — Streamlit**

```bat
conda activate npk_ui
cd /d "C:\Users\LENOVO\Downloads\Manjitha_NPK_Dose_Studio"
python -m streamlit run frontend/app.py --server.port 8501
```

4. Open:
   - Dashboard: http://127.0.0.1:8501
   - Interactive API docs: http://127.0.0.1:8071/docs
   - API health: http://127.0.0.1:8071/health

Alternatively, after installing dependencies, run `START_WINDOWS.bat` from a Windows installation that has `conda` accessible. For troubleshooting, use the two manual terminals above.

### Run the backend with Docker

Install and start Docker Desktop, then run these commands from the `NPK_Mix_Model` folder. Docker builds only the FastAPI backend; the Streamlit dashboard remains a separate service.

```powershell
docker build -f backend/Dockerfile -t nutrientos-npk-api backend
docker run --rm -d --name nutrientos-npk-api -p 8071:8071 nutrientos-npk-api
```

Check the API at http://127.0.0.1:8071/health and open the dashboard at http://127.0.0.1:8501 after starting Streamlit separately. Stop the API container with:

```powershell
docker stop nutrientos-npk-api
```

### Folder layout

```text
Manjitha_NPK_Dose_Studio/
├── backend/
│   ├── __init__.py
│   ├── Dockerfile              FastAPI backend container
│   ├── main.py                 FastAPI REST endpoints
│   ├── requirements.txt        Backend-only dependencies
│   └── science.py              Scientifically separated reference/simulation calculator
├── frontend/
│   ├── __init__.py
│   └── app.py                  Modern Streamlit dashboard
├── tests/
│   └── test_science.py        Verified calculation tests
├── docs/
│   └── MODEL_NOTES.md         Scientific design and road map
├── requirements.txt
├── INSTALL_WINDOWS.bat
├── START_WINDOWS.bat
├── RUN_API.bat
├── RUN_DASHBOARD.bat
└── README.md
```

## Features

- Professional Streamlit dashboard with elegant dark-green visual system, field inputs, interactive charts, crop-photo preview, research traceability and JSON/CSV downloads.
- Dummy **N**, **P**, **K** values in mg/kg plus optional pH display. No sensors are required.
- Reference application schedule from **Sri Lanka Department of Agriculture field chilli** guidance, correctly expressed as **Urea, TSP, MOP product weights in kg/ha** then converted to grams for a chosen plot and per-stage amounts.
- Explicit stage selection at basal, weeks 2, 4, 8, 12 and 16.
- Enter a *single* fixed-composition NPK liquid, with N–P₂O₅–K₂O label percentages (w/w), measured **density** in g/mL and dilution factor.
- Optional experimental user-supplied soil-calibration coefficients. Without all three explicit coefficients, the backend refuses to produce a soil-adjusted dose preview.
- With coefficients, mathematical demonstration of one liquid volume against three **modelled fertilizer-equivalent targets**. The simulator predicts mismatch because one liquid cannot independently adjust N/P/K.
- No pump commands. All results carry a research-only warning. Future real sensor integration would change telemetry inputs but must not bypass agronomy validation.

## What the calculations actually mean

### A. Reliable reference calculation — no soil adjustment

DOA Sri Lankan field chilli reference (mass of fertilizer product, not mass of nutrient):

| Application | Urea kg/ha | TSP kg/ha | MOP kg/ha |
|---|---:|---:|---:|
| Basal | 0 | 100 | 50 |
| Week 2 | 100 | 0 | 0 |
| Week 4 | 125 | 0 | 0 |
| Week 8 | 125 | 0 | 50 |
| Week 12 | 125 | 0 | 0 |
| Week 16 | 125 | 0 | 0 |
| Whole season | 600 | 100 | 100 |

The mass scaled to your plot is `kg/ha × plot_m2 / 10,000 × 1,000 = grams of fertilizer product for the plot`. This does not claim soil-tailored crop need.

Approximate nutrient fractions in the reference **solid products** (must verify actual bag label): Urea 46% N, TSP 46% P₂O₅, MOP 60% K₂O. These define **fertilizer nutrient-equivalent inputs**, not measured physiological demand.

### B. Experimental soil-budget demonstration — not validated agronomy

`soil_contribution_N (kg/ha) = soil_reading_N(mg/kg) × entered_N_transfer_coefficient`

`soil_contribution_P2O5 (kg/ha) = soil_P(mg/kg) × entered_P2O5_transfer_coefficient`

`soil_contribution_K2O (kg/ha) = soil_K(mg/kg) × entered_K2O_transfer_coefficient`

The input *transfer coefficients* are not universal and must be derived/validated for the particular soil assay, crop, locality and period. The P/K transfer coefficients already include the elemental-to-oxide basis conversion and availability model. **Do not invent or copy them across different soils.** The example UI inputs are synthetic demonstration values only and are locked out until the user explicitly opts into the experimental mode.

To avoid subtracting existing soil nutrients repeatedly every week, the simulated soil contribution is subtracted **once from a whole-season reference nutrient input**, then the remaining seasonal fertilizer-equivalent input is distributed in proportion to the stage schedule. This is for software testing, **not** a locally validated STCR crop response equation. An actual STCR model requires field-response datasets and validated coefficients; it is not simply the above subtraction.

### C. One fixed-ratio liquid comparison

If the bottle has N-P₂O₅-K₂O `5-5-5` **by weight** and a verified density of `1.10 g/mL`, the undiluted solution contains `0.055 g/mL` of each listed nutrient. If diluted 10-fold by final solution volume, this becomes approximately `0.0055 g/mL` of each. Correct actual stock concentration and mix compatibility must be confirmed by the manufacturer/lab.

For research **comparison only**, the app finds a nonnegative volume `V` minimizing:

`sum over nutrients j of (concentration_j [g/mL] × V [mL] - modelled_target_j [g])²`

`V* = max(0, sum(c_j × target_j) / sum(c_j²))` if any nutrient is present.

Because one liquid has a fixed ratio, the app shows each nutrient's **shortfall or oversupply**. This is an unweighted mathematical fit, **not** a scientifically validated crop dose. `pump_target_ml` is always null; `pump_enabled` is always false.

## Tests

```bat
python -m pytest -q
```

## API

- `GET /health`
- `GET /api/v1/config`
- `GET /api/v1/sensor-demo`
- `POST /api/v1/calculate`

Import `NutrientOS_Frontend_API.postman_collection.json` into Postman to try only the two endpoints used by the Streamlit frontend (`GET /health` and `POST /api/v1/calculate`). It uses `http://127.0.0.1:8071` as its `baseUrl` variable; start the FastAPI backend before sending requests. `NutrientOS_NPK_Model.postman_collection.json` contains the broader set of API examples.

Example request (also visible in FastAPI `/docs`):

```json
{
  "plot": {"area": 10, "unit": "m2", "plants": 20, "stage_week": 4},
  "soil": {"n_mgkg": 80, "p_mgkg": 12, "k_mgkg": 90, "ph": 6.3, "origin": "SIMULATED"},
  "liquid": {"label_n_percent": 5, "label_p2o5_percent": 5, "label_k2o_percent": 5, "density_g_ml": 1.10, "dilution_factor": 1},
  "calculation_mode": "reference"
}
```

## References

1. Sri Lanka DOA, **Field Crops – Chilli – Sinhala** (the field chilli schedule, not HORDI capsicum): https://doa.gov.lk/field-crops-chilli-si/
2. Maragani et al. (2023), **Balanced Nutrient Recommendations for Dry Chilli in an Inceptisol of Tamil Nadu based on a Targeted Yield Model**, DOI: https://doi.org/10.18805/ag.D-5782. A study of Indian conditions, **not local coefficient validation**.

## Next actual research milestone

Collect paired calibrated N/P/K soil observations (with exact analytical units/method), fertilizer application data, growth-stage/yield outcomes and treatment controls for local Sri Lankan chilli, then estimate and validate a statistical crop-response model. Publish model uncertainty and compare against the unadjusted DOA benchmark. Avoid presenting the mock-coefficient demo as an AI-trained fertilizer recommendation.
