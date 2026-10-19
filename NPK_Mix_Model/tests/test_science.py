import math
import pytest
from pydantic import ValidationError
from backend.science import DoseRequest, Plot, Soil, Liquid, Calibration, calculate


def test_reference_scales_10_square_metres():
    result = calculate(DoseRequest(plot=Plot(area=10, unit="m2", plants=20, stage_week=4)))
    # 125 kg/ha of urea in week 4 -> 125 g / 10 m2
    assert result["reference"]["stage_product_g_plot"]["urea"] == 125.0
    assert result["reference"]["stage_product_g_plot"]["tsp"] == 0
    assert result["status"] == "DOA_REFERENCE_ONLY"
    assert result["modelled"]["liquid_comparison"] is None


def test_season_total_matches_doa():
    r = calculate(DoseRequest())
    assert r["reference"]["season_product_kg_ha"] == {"urea": 600, "tsp": 100, "mop": 100}


def test_dummy_sensor_reference_mode_never_changes_output():
    a = calculate(DoseRequest(soil=Soil(n_mgkg=5, p_mgkg=5, k_mgkg=5)))
    b = calculate(DoseRequest(soil=Soil(n_mgkg=500, p_mgkg=500, k_mgkg=500)))
    assert a["reference"] == b["reference"]
    assert a["modelled"] == b["modelled"]


def test_research_without_coefficients_refuses_dose():
    r = calculate(DoseRequest(calculation_mode="experimental_soil"))
    assert r["modelled"]["liquid_comparison"] is None
    assert r["status"] == "SOIL_CALIBRATION_REQUIRED"


def test_experimental_changes_with_soil_n_and_never_activates_pump():
    cal = Calibration(n_kg_ha_per_mgkg=0.2, p2o5_kg_ha_per_mgkg=0.5, k2o_kg_ha_per_mgkg=0.35,
                      provenance="TEST FIXTURE NOT VALIDATED")
    lo = calculate(DoseRequest(calculation_mode="experimental_soil", calibration=cal, soil=Soil(n_mgkg=20)))
    hi = calculate(DoseRequest(calculation_mode="experimental_soil", calibration=cal, soil=Soil(n_mgkg=200)))
    assert lo["modelled"]["liquid_comparison"]["comparison_volume_ml"] > hi["modelled"]["liquid_comparison"]["comparison_volume_ml"]
    assert hi["modelled"]["liquid_comparison"]["pump_enabled"] is False
    assert hi["modelled"]["liquid_comparison"]["pump_target_ml"] is None


def test_one_mix_can_generate_phosphorus_surplus():
    cal = Calibration(n_kg_ha_per_mgkg=0, p2o5_kg_ha_per_mgkg=0, k2o_kg_ha_per_mgkg=0)
    r = calculate(DoseRequest(calculation_mode="experimental_soil", calibration=cal,
                              plot=Plot(stage_week=4), liquid=Liquid(label_n_percent=5, label_p2o5_percent=5, label_k2o_percent=5)))
    assert r["modelled"]["liquid_comparison"]["nutrients_delivered_g"]["P2O5"] > 0
    assert any("P2O5" in msg for msg in r["modelled"]["liquid_comparison"]["constraints"])


def test_percentages_are_mass_weight_not_elemental():
    cal = Calibration(n_kg_ha_per_mgkg=0, p2o5_kg_ha_per_mgkg=0, k2o_kg_ha_per_mgkg=0)
    r = calculate(DoseRequest(calculation_mode="experimental_soil", calibration=cal,
                              liquid=Liquid(label_n_percent=10, label_p2o5_percent=0, label_k2o_percent=0,
                                            density_g_ml=1.2, dilution_factor=2)))
    assert r["modelled"]["liquid_comparison"]["grams_per_ml"]["N"] == 0.06


def test_invalid_percentages_rejected():
    with pytest.raises(ValidationError):
        Liquid(label_n_percent=50, label_p2o5_percent=40, label_k2o_percent=20)


def test_area_units_equivalent():
    a = calculate(DoseRequest(plot=Plot(area=10000, unit="m2")))
    b = calculate(DoseRequest(plot=Plot(area=1, unit="hectare")))
    assert a["reference"] == b["reference"]


def test_baseline_has_no_active_pump_command():
    r = calculate(DoseRequest())
    assert r["modelled"]["liquid_comparison"] is None
