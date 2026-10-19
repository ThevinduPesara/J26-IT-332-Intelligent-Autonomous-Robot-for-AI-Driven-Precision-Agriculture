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


