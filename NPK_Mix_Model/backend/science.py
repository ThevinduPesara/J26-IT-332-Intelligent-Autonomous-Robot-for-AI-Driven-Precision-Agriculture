"""Chilli nutrient dose research demonstrator.

The soil-to-plant coefficients are operator-supplied and unvalidated. This
module is for comparison only and never controls dosing hardware.
"""

from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, Field, model_validator

DOA_URL = "https://doa.gov.lk/field-crops-chilli-si/"
RESEARCH_URL = "https://doi.org/10.18805/ag.D-5782"
SOURCE_NOTE = (
    "Sri Lanka Department of Agriculture, Field Crops – Chilli "
    "(field chilli, not capsicum)."
)
SCHEDULE = (
    {"week": 0, "stage": "Basal – before transplanting", "urea": 0.0, "tsp": 100.0, "mop": 50.0},
    {"week": 2, "stage": "Week 02 – top dressing", "urea": 100.0, "tsp": 0.0, "mop": 0.0},
    {"week": 4, "stage": "Week 04 – top dressing", "urea": 125.0, "tsp": 0.0, "mop": 0.0},
    {"week": 8, "stage": "Week 08 – top dressing", "urea": 125.0, "tsp": 0.0, "mop": 50.0},
    {"week": 12, "stage": "Week 12 – top dressing", "urea": 125.0, "tsp": 0.0, "mop": 0.0},
    {"week": 16, "stage": "Week 16 – top dressing", "urea": 125.0, "tsp": 0.0, "mop": 0.0},
)
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
    n_mgkg: float = Field(default=80.0, ge=0, le=100_000)
    p_mgkg: float = Field(default=12.0, ge=0, le=100_000)
    k_mgkg: float = Field(default=90.0, ge=0, le=100_000)
    ph: float | None = Field(default=6.3, ge=0, le=14)
    origin: Literal["SIMULATED", "MANUAL_UNVERIFIED"] = "SIMULATED"


class Liquid(BaseModel):
    """Guaranteed analysis percentages are N-P2O5-K2O by mass, not N-P-K."""

    label_n_percent: float = Field(default=5.0, ge=0, le=100)
    label_p2o5_percent: float = Field(default=5.0, ge=0, le=100)
    label_k2o_percent: float = Field(default=5.0, ge=0, le=100)
    density_g_ml: float = Field(default=1.1, gt=0, le=3)
    dilution_factor: float = Field(default=1.0, ge=1, le=10_000)

    @model_validator(mode="after")
    def composition_limit(self) -> "Liquid":
        if self.label_n_percent + self.label_p2o5_percent + self.label_k2o_percent > 100:
            raise ValueError("The three guaranteed-analysis percentages cannot sum above 100%")
        return self


class Calibration(BaseModel):
    """Unvalidated soil reading-to-available-nutrient transfer coefficients."""

    n_kg_ha_per_mgkg: float | None = Field(default=None, ge=0, le=100)
    p2o5_kg_ha_per_mgkg: float | None = Field(default=None, ge=0, le=100)
    k2o_kg_ha_per_mgkg: float | None = Field(default=None, ge=0, le=100)
    provenance: str = Field(default="", max_length=1000)

    def complete(self) -> bool:
        return all(
            value is not None
            for value in (
                self.n_kg_ha_per_mgkg,
                self.p2o5_kg_ha_per_mgkg,
                self.k2o_kg_ha_per_mgkg,
            )
        )


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


def _scale(values: dict[str, float], factor: float) -> dict[str, float]:
    return {key: value * factor for key, value in values.items()}


def _round(values: dict[str, float], digits: int = 5) -> dict[str, float]:
    return {key: round(value, digits) for key, value in values.items()}


def _status(request: DoseRequest) -> str:
    if request.calculation_mode == "reference":
        return "DOA_REFERENCE_ONLY"
    if not request.calibration.complete():
        return "SOIL_CALIBRATION_REQUIRED"
    return "EXPERIMENTAL_USER_COEFFICIENTS_NOT_VERIFIED"


def _experimental_need(
    request: DoseRequest,
    season: dict[str, float],
    stage: dict[str, float],
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    calibration = request.calibration
    soil = request.soil
    soil_contribution = {
        "N": soil.n_mgkg * calibration.n_kg_ha_per_mgkg,
        "P2O5": soil.p_mgkg * calibration.p2o5_kg_ha_per_mgkg,
        "K2O": soil.k_mgkg * calibration.k2o_kg_ha_per_mgkg,
    }
    seasonal_residual = {
        nutrient: max(0.0, season[nutrient] - soil_contribution[nutrient])
        for nutrient in NUTRIENTS
    }
    stage_input = {
        nutrient: (
            seasonal_residual[nutrient] * stage[nutrient] / season[nutrient]
            if season[nutrient] > 0
            else 0.0
        )
        for nutrient in NUTRIENTS
    }
    return soil_contribution, seasonal_residual, stage_input


def _liquid_preview(deficit_g: dict[str, float], liquid: Liquid) -> dict:
    labels = {
        "N": liquid.label_n_percent,
        "P2O5": liquid.label_p2o5_percent,
        "K2O": liquid.label_k2o_percent,
    }
    grams_per_ml = {
        nutrient: percent / 100 * liquid.density_g_ml / liquid.dilution_factor
        for nutrient, percent in labels.items()
    }
    norm_squared = sum(value * value for value in grams_per_ml.values())
    dot = sum(deficit_g[nutrient] * grams_per_ml[nutrient] for nutrient in NUTRIENTS)
    volume_ml = max(0.0, dot / norm_squared) if norm_squared > 0 else None
    supplied = (
        {nutrient: volume_ml * grams_per_ml[nutrient] for nutrient in NUTRIENTS}
        if volume_ml is not None
        else {nutrient: 0.0 for nutrient in NUTRIENTS}
    )
    residual = {
        nutrient: deficit_g[nutrient] - supplied[nutrient]
        for nutrient in NUTRIENTS
    }
    cautions = []
    if volume_ml is None:
        cautions.append("The selected liquid contains no N, P2O5 or K2O; no volume can be calculated.")
    else:
        for nutrient, difference in residual.items():
            if difference < -1e-7:
                cautions.append(
                    f"{nutrient}: fixed-ratio liquid exceeds the modelled target by {abs(difference):.3f} g."
                )
            elif difference > 1e-7:
                cautions.append(
                    f"{nutrient}: the single mixture leaves a modelled shortfall of {difference:.3f} g."
                )
    return {
        "comparison_volume_ml": round(volume_ml, 4) if volume_ml is not None else None,
        "per_plant_comparison_ml": None,
        "grams_per_ml": _round(grams_per_ml),
        "nutrients_delivered_g": _round(supplied),
        "nutrient_difference_g_target_minus_delivered": _round(residual),
        "constraints": cautions,
        "optimizer": "Nonnegative unweighted least-squares (one fixed-ratio liquid; model comparison only)",
        "pump_target_ml": None,
        "pump_enabled": False,
    }


def calculate(request: DoseRequest) -> dict:
    area_m2 = request.plot.area * UNITS_M2[request.plot.unit]
    area_ratio = area_m2 / 10_000
    product_names = ("urea", "tsp", "mop")
    season_products = {
        name: sum(item[name] for item in SCHEDULE)
        for name in product_names
    }
    season_nutrients = _nutrients_from_product(**season_products)
    stage = next(item for item in SCHEDULE if item["week"] == request.plot.stage_week)
    stage_nutrients = _nutrients_from_product(
        stage["urea"], stage["tsp"], stage["mop"]
    )
    schedule = []
    for item in SCHEDULE:
        products_for_plot = _scale(
            {name: item[name] for name in product_names}, area_ratio * 1000
        )
        due_date = (
            (request.plot.transplant_date + timedelta(weeks=item["week"])).isoformat()
            if request.plot.transplant_date
            else None
        )
        nutrients_for_plot = _scale(
            _nutrients_from_product(item["urea"], item["tsp"], item["mop"]),
            area_ratio * 1000,
        )
        schedule.append(
            {
                "week": item["week"],
                "stage": item["stage"],
                "due_date": due_date,
                "reference_products_kg_ha": {
                    name: item[name] for name in product_names
                },
                "reference_products_g_for_plot": _round(products_for_plot),
                "reference_nutrients_g_for_plot": _round(nutrients_for_plot),
            }
        )

    soil_supply = seasonal_remaining = stage_modelled = liquid_result = None
    mode_status = _status(request)
    if request.calculation_mode == "experimental_soil" and request.calibration.complete():
        soil_supply, seasonal_remaining, stage_modelled = _experimental_need(
            request, season_nutrients, stage_nutrients
        )
        desired_plot_g = _scale(stage_modelled, area_ratio * 1000)
        liquid_result = _liquid_preview(desired_plot_g, request.liquid)
        if liquid_result["comparison_volume_ml"] is not None:
            liquid_result["per_plant_comparison_ml"] = round(
                liquid_result["comparison_volume_ml"] / request.plot.plants, 4
            )

    stage_schedule = schedule[next(
        index for index, item in enumerate(SCHEDULE)
        if item["week"] == request.plot.stage_week
    )]
    return {
        "status": mode_status,
        "source": SOURCE_NOTE,
        "source_url": DOA_URL,
        "research_method_url": RESEARCH_URL,
        "plot": {
            "area_m2": round(area_m2, 5),
            "plants": request.plot.plants,
            "stage_week": request.plot.stage_week,
        },
        "soil": request.soil.model_dump(),
        "liquid": request.liquid.model_dump(),
        "mode": request.calculation_mode,
        "reference": {
            "schedule": schedule,
            "season_product_kg_ha": _round(season_products),
            "season_product_g_plot": _round(_scale(season_products, area_ratio * 1000)),
            "season_nutrient_kg_ha": _round(season_nutrients),
            "stage_product_g_plot": stage_schedule["reference_products_g_for_plot"],
            "stage_nutrient_g_plot": stage_schedule["reference_nutrients_g_for_plot"],
            "stage_date": stage_schedule["due_date"],
        },
        "modelled": {
            "calibration": (
                request.calibration.model_dump()
                if request.calculation_mode == "experimental_soil"
                else None
            ),
            "estimated_soil_contribution_kg_ha": (
                _round(soil_supply) if soil_supply is not None else None
            ),
            "residual_season_nutrient_kg_ha": (
                _round(seasonal_remaining) if seasonal_remaining is not None else None
            ),
            "stage_target_nutrient_g_plot": (
                _round(_scale(stage_modelled, area_ratio * 1000))
                if stage_modelled is not None
                else None
            ),
            "liquid_comparison": liquid_result,
        },
        "warnings": [
            "EDUCATIONAL / RESEARCH PROTOTYPE ONLY – not approved for application or dispensing.",
            "DOA reference uses solid Urea, TSP and MOP masses; these are not directly interchangeable with any liquid NPK formulation.",
            "Sensor mg/kg cannot be directly subtracted from kg/ha. A validated soil-to-plant-availability model is required.",
            "The research-mode coefficients are supplied by the user. Neither the code nor the source validates them for Sri Lankan soil.",
            "A single fixed-ratio NPK liquid cannot independently satisfy all three nutrient targets; inspect surpluses and shortfalls.",
            "No physical pump actuation is implemented. Always seek agronomic and product-label review before use.",
        ],
    }


def demo_request() -> DoseRequest:
    return DoseRequest()
