"""Chilli nutrient dose research demonstrator.

CAUTION: Formula demo is not an agronomically validated recommendation.
Reference schedule: Sri Lanka DOA field chilli, product kg/ha, not pure nutrients.
No dosing hardware is controlled by this software.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Literal
import math

from pydantic import BaseModel, Field, model_validator

DOA_URL = "https://doa.gov.lk/field-crops-chilli-si/"
RESEARCH_URL = "https://doi.org/10.18805/ag.D-5782"
SOURCE_NOTE = "Sri Lanka Department of Agriculture, Field Crops – Chilli (field chilli, not capsicum)."

# Application-stage product weights (kg / hectare), read from the cited DOA source.
SCHEDULE = (
    {"week": 0, "stage": "Basal · before transplanting", "urea": 0.0, "tsp": 100.0, "mop": 50.0},
    {"week": 2, "stage": "Week 02 · top dressing", "urea": 100.0, "tsp": 0.0, "mop": 0.0},
    {"week": 4, "stage": "Week 04 · top dressing", "urea": 125.0, "tsp": 0.0, "mop": 0.0},
    {"week": 8, "stage": "Week 08 · top dressing", "urea": 125.0, "tsp": 0.0, "mop": 50.0},
    {"week": 12, "stage": "Week 12 · top dressing", "urea": 125.0, "tsp": 0.0, "mop": 0.0},
    {"week": 16, "stage": "Week 16 · top dressing", "urea": 125.0, "tsp": 0.0, "mop": 0.0},
)

# Illustrative representative fertilizer analyses; verify actual label before using.
REFERENCE_FRACTIONS = {"urea": 0.46, "tsp": 0.46, "mop": 0.60}
UNITS_M2 = {"m2": 1.0, "perch": 25.29285264, "acre": 4046.8564224, "hectare": 10000.0}
NUTRIENTS = ("N", "P2O5", "K2O")


class Plot(BaseModel):
    area: float = Field(default=10.0, gt=0, le=1_000_000)
    unit: Literal["m2", "perch", "acre", "hectare"] = "m2"
    plants: int = Field(default=20, ge=1, le=1_000_000)
    stage_week: Literal[0, 2, 4, 8, 12, 16] = 4
    transplant_date: date | None = None


class Soil(BaseModel):
    n_mgkg: float = Field(default=80.0, ge=0, le=100000)
    p_mgkg: float = Field(default=12.0, ge=0, le=100000)
    k_mgkg: float = Field(default=90.0, ge=0, le=100000)
    ph: float | None = Field(default=6.3, ge=0, le=14)
    origin: Literal["SIMULATED", "MANUAL_UNVERIFIED"] = "SIMULATED"


class Liquid(BaseModel):
    """Labels N-P2O5-K2O, mass percent (w/w), not P or K elemental."""
    label_n_percent: float = Field(default=5.0, ge=0, le=100)
    label_p2o5_percent: float = Field(default=5.0, ge=0, le=100)
    label_k2o_percent: float = Field(default=5.0, ge=0, le=100)
    density_g_ml: float = Field(default=1.10, gt=0, le=3)
    dilution_factor: float = Field(default=1.0, ge=1, le=10000)

    @model_validator(mode="after")
    def composition_limit(self):
        if sum((self.label_n_percent, self.label_p2o5_percent, self.label_k2o_percent)) > 100:
            raise ValueError("The three guaranteed-analysis percentages cannot sum above 100%")
        return self


class Calibration(BaseModel):
    """Operator-supplied demo transfer coefficients, NOT universal agronomic factors.

    Units: nutrient kg/ha available to the crop per mg/kg of the respective
    soil sensor's N, P or K reading. P and K coefficients are expressed in
    P2O5 and K2O fertilizer-equivalent nutrient units, respectively.
    No default coefficients are taken from published studies.
    """
    n_kg_ha_per_mgkg: float | None = Field(default=None, ge=0, le=100)
    p2o5_kg_ha_per_mgkg: float | None = Field(default=None, ge=0, le=100)
    k2o_kg_ha_per_mgkg: float | None = Field(default=None, ge=0, le=100)
    provenance: str = Field(default="", max_length=1000)

    def complete(self) -> bool:
        return all(v is not None for v in (
            self.n_kg_ha_per_mgkg,
            self.p2o5_kg_ha_per_mgkg,
            self.k2o_kg_ha_per_mgkg,
        ))


class DoseRequest(BaseModel):
    plot: Plot = Field(default_factory=Plot)
    soil: Soil = Field(default_factory=Soil)
    liquid: Liquid = Field(default_factory=Liquid)
    calculation_mode: Literal["reference", "experimental_soil"] = "reference"
    calibration: Calibration = Field(default_factory=Calibration)


def _nutrients_from_product(urea: float, tsp: float, mop: float) -> dict[str, float]:
    return {
        "N": urea * REFERENCE_FRACTIONS["urea"],
        "P2O5": tsp * REFERENCE_FRACTIONS["tsp"],
        "K2O": mop * REFERENCE_FRACTIONS["mop"],
    }


def _scale(d: dict[str, float], factor: float) -> dict[str, float]:
    return {k: v * factor for k, v in d.items()}


def _round(d: dict[str, float], digits: int = 5) -> dict[str, float]:
    return {k: round(v, digits) for k, v in d.items()}


def _status(req: DoseRequest) -> str:
    if req.calculation_mode == "reference":
        return "DOA_REFERENCE_ONLY"
    if not req.calibration.complete():
        return "SOIL_CALIBRATION_REQUIRED"
    return "EXPERIMENTAL_USER_COEFFICIENTS_NOT_VERIFIED"


def _experimental_need(req: DoseRequest, season: dict[str, float], stage: dict[str, float]):
    c = req.calibration
    soil = req.soil
    soil_contribution = {
        "N": soil.n_mgkg * c.n_kg_ha_per_mgkg,
        "P2O5": soil.p_mgkg * c.p2o5_kg_ha_per_mgkg,
        "K2O": soil.k_mgkg * c.k2o_kg_ha_per_mgkg,
    }
    # Important: subtract only once over the *whole season*, not again each week.
    seasonal_residual = {n: max(0.0, season[n] - soil_contribution[n]) for n in NUTRIENTS}
    # Allocate the experimental remaining seasonal input using reference application shares.
    stage_input = {
        n: (seasonal_residual[n] * stage[n] / season[n] if season[n] > 0 else 0.0)
        for n in NUTRIENTS
    }
    return soil_contribution, seasonal_residual, stage_input


def _liquid_preview(deficit_g: dict[str, float], liquid: Liquid) -> dict:
    """Nonnegative least-squares fit of one fixed-ratio solution to 3 targets.

    Minimizes sum_i (c_i*volume_ml - target_g_i)^2, volume_ml >= 0.
    This is an engineering comparison, NOT an authorized fertilizer prescription.
    """
    labels = {
        "N": liquid.label_n_percent,
        "P2O5": liquid.label_p2o5_percent,
        "K2O": liquid.label_k2o_percent,
    }
    grams_per_ml = {
        n: (p / 100.0) * liquid.density_g_ml / liquid.dilution_factor
        for n, p in labels.items()
    }
    norm2 = sum(v * v for v in grams_per_ml.values())
    dot = sum(grams_per_ml[n] * deficit_g[n] for n in NUTRIENTS)
    volume_ml = max(0.0, dot / norm2) if norm2 > 0 else None
    supplied = ({n: volume_ml * grams_per_ml[n] for n in NUTRIENTS}
                if volume_ml is not None else {n: 0 for n in NUTRIENTS})
    residual = {n: deficit_g[n] - supplied[n] for n in NUTRIENTS}
    cautions = []
    if volume_ml is None:
        cautions.append("The selected liquid contains no N, P2O5 or K2O; no volume can be calculated.")
    else:
        for n in NUTRIENTS:
            if residual[n] < -1e-7:
                cautions.append(f"{n}: fixed-ratio liquid exceeds the modelled target by {-residual[n]:.3f} g.")
            elif residual[n] > 1e-7:
                cautions.append(f"{n}: the single mixture leaves a modelled shortfall of {residual[n]:.3f} g.")
    return {
        "comparison_volume_ml": round(volume_ml, 4) if volume_ml is not None else None,
        "per_plant_comparison_ml": round(volume_ml / 1, 4) if volume_ml is not None else None,
        "grams_per_ml": _round(grams_per_ml, 7),
        "nutrients_delivered_g": _round(supplied),
        "nutrient_difference_g_target_minus_delivered": _round(residual),
        "constraints": cautions,
        "optimizer": "Nonnegative unweighted least-squares (one fixed-ratio liquid; model comparison only)",
        "pump_target_ml": None,
        "pump_enabled": False,
    }


def calculate(req: DoseRequest) -> dict:
    area_m2 = req.plot.area * UNITS_M2[req.plot.unit]
    area_ratio = area_m2 / 10_000.0
    totals = {name: sum(s[name] for s in SCHEDULE) for name in ("urea", "tsp", "mop")}
    season_nutrients_kg_ha = _nutrients_from_product(**totals)

    stage = next(s for s in SCHEDULE if s["week"] == req.plot.stage_week)
    stage_nutrients_kg_ha = _nutrients_from_product(stage["urea"], stage["tsp"], stage["mop"])
    schedule = []
    for s in SCHEDULE:
        mass = _scale({k: s[k] for k in ("urea", "tsp", "mop")}, area_ratio * 1000)
        due = None
        if req.plot.transplant_date is not None:
            due = (req.plot.transplant_date + timedelta(weeks=s["week"])).isoformat()
        schedule.append({
            "week": s["week"], "stage": s["stage"], "due_date": due,
            "reference_products_kg_ha": {k: s[k] for k in ("urea", "tsp", "mop")},
            "reference_products_g_for_plot": _round(mass),
            "reference_nutrients_g_for_plot": _round(_scale(
                _nutrients_from_product(s["urea"], s["tsp"], s["mop"]), area_ratio * 1000)),
        })

    mode_status = _status(req)
    soil_supply = None
    seasonal_remaining = None
    stage_modelled = None
    liquid_result = None
    if req.calculation_mode == "experimental_soil" and req.calibration.complete():
        soil_supply, seasonal_remaining, stage_modelled = _experimental_need(
            req, season_nutrients_kg_ha, stage_nutrients_kg_ha
        )
        desired_plot_g = _scale(stage_modelled, area_ratio * 1000)
        liquid_result = _liquid_preview(desired_plot_g, req.liquid)
        if liquid_result["comparison_volume_ml"] is not None:
            v = liquid_result["comparison_volume_ml"]
            liquid_result["per_plant_comparison_ml"] = round(v / req.plot.plants, 4)
    elif req.calculation_mode == "reference":
        # The DOA quantities are Urea/TSP/MOP masses, NOT an instruction to
        # substitute one liquid at the same apparent NPK nutrient concentration.
        pass

    return {
        "status": mode_status,
        "source": SOURCE_NOTE,
        "source_url": DOA_URL,
        "research_method_url": RESEARCH_URL,
        "plot": {"area_m2": round(area_m2, 5), "plants": req.plot.plants, "stage_week": req.plot.stage_week},
        "soil": req.soil.model_dump(),
        "liquid": req.liquid.model_dump(),
        "mode": req.calculation_mode,
        "reference": {
            "schedule": schedule,
            "season_product_kg_ha": _round(totals),
            "season_product_g_plot": _round(_scale(totals, area_ratio * 1000)),
            "season_nutrient_kg_ha": _round(season_nutrients_kg_ha),
            "stage_product_g_plot": _round(_scale({k: stage[k] for k in totals}, area_ratio * 1000)),
            "stage_nutrient_g_plot": _round(_scale(stage_nutrients_kg_ha, area_ratio * 1000)),
            "stage_date": schedule[[r["week"] for r in schedule].index(req.plot.stage_week)]["due_date"],
        },
        "modelled": {
            "calibration": req.calibration.model_dump() if req.calculation_mode == "experimental_soil" else None,
            "estimated_soil_contribution_kg_ha": _round(soil_supply) if soil_supply else None,
            "residual_season_nutrient_kg_ha": _round(seasonal_remaining) if seasonal_remaining else None,
            "stage_target_nutrient_g_plot": _round(_scale(stage_modelled, area_ratio * 1000)) if stage_modelled else None,
            "liquid_comparison": liquid_result,
        },
        "warnings": [
            "EDUCATIONAL / RESEARCH PROTOTYPE ONLY — not approved for application or dispensing.",
            "DOA reference uses solid Urea, TSP and MOP masses; these are not directly interchangeable with any liquid NPK formulation.",
            "Sensor mg/kg cannot be directly subtracted from kg/ha. A validated soil-to-plant-availability model is required.",
            "The research-mode coefficients are supplied by the user. Neither the code nor the source validates them for Sri Lankan soil.",
            "A single fixed-ratio NPK liquid cannot independently satisfy all three nutrient targets; inspect surpluses and shortfalls.",
            "No physical pump actuation is implemented. Always seek agronomic and product-label review before use.",
        ],
    }


