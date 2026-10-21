const API_BASE_URL =
  process.env.NEXT_PUBLIC_NPK_API_URL || "http://127.0.0.1:8501";

export interface NpkPlot {
  area: number;
  unit: "m2" | "perch" | "acre" | "hectare";
  plants: number;
  stage_week: 0 | 2 | 4 | 8 | 12 | 16;
  transplant_date: string | null;
}

export interface NpkSoil {
  n_mgkg: number;
  p_mgkg: number;
  k_mgkg: number;
  ph: number | null;
  origin: "SIMULATED" | "MANUAL_UNVERIFIED";
}

export interface NpkLiquid {
  label_n_percent: number;
  label_p2o5_percent: number;
  label_k2o_percent: number;
  density_g_ml: number;
  dilution_factor: number;
}

export interface NpkCalibration {
  n_kg_ha_per_mgkg: number | null;
  p2o5_kg_ha_per_mgkg: number | null;
  k2o_kg_ha_per_mgkg: number | null;
  provenance: string;
}

export interface NpkRequest {
  plot: NpkPlot;
  soil: NpkSoil;
  liquid: NpkLiquid;
  calculation_mode: "reference" | "experimental_soil";
  calibration: NpkCalibration;
}

export interface NpkConfig {
  crop: string;
  source_url: string;
  schedule_kg_ha: Array<{
    week: number;
    stage: string;
    urea: number;
    tsp: number;
    mop: number;
  }>;
  demo: NpkRequest;
  dose_requires_user_calibration: boolean;
  physical_actuation: boolean;
}

export interface NpkSensorDemo extends NpkSoil {
  not_sensor_measurements: boolean;
}

export type NutrientValues = Record<"N" | "P2O5" | "K2O", number>;

export interface NpkCalculationResponse {
  status: string;
  source: string;
  source_url: string;
  research_method_url: string;
  plot: {
    area_m2: number;
    plants: number;
    stage_week: number;
  };
  soil: NpkSoil;
  liquid: NpkLiquid;
  mode: "reference" | "experimental_soil";
  reference: {
    schedule: Array<{
      week: number;
      stage: string;
      due_date: string | null;
      reference_products_kg_ha: Record<"urea" | "tsp" | "mop", number>;
      reference_products_g_for_plot: Record<"urea" | "tsp" | "mop", number>;
      reference_nutrients_g_for_plot: NutrientValues;
    }>;
    season_product_kg_ha: Record<"urea" | "tsp" | "mop", number>;
    season_product_g_plot: Record<"urea" | "tsp" | "mop", number>;
    season_nutrient_kg_ha: NutrientValues;
    stage_product_g_plot: Record<"urea" | "tsp" | "mop", number>;
    stage_nutrient_g_plot: NutrientValues;
    stage_date: string | null;
  };
  modelled: {
    calibration: NpkCalibration | null;
    estimated_soil_contribution_kg_ha: NutrientValues | null;
    residual_season_nutrient_kg_ha: NutrientValues | null;
    stage_target_nutrient_g_plot: NutrientValues | null;
    liquid_comparison: {
      comparison_volume_ml: number | null;
      per_plant_comparison_ml: number | null;
      grams_per_ml: NutrientValues;
      nutrients_delivered_g: NutrientValues;
      nutrient_difference_g_target_minus_delivered: NutrientValues;
      constraints: string[];
      optimizer: string;
      pump_target_ml: number | null;
      pump_enabled: false;
    } | null;
  };
  warnings: string[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(
      "NPK backend is unavailable. Start the API at http://127.0.0.1:8501 and try again."
    );
  }

  if (!response.ok) {
    let detail = `NPK backend returned HTTP ${response.status}`;
    try {
      const body: { detail?: string | Array<{ msg?: string }> } =
        await response.json();
      if (typeof body.detail === "string") detail = body.detail;
      else if (Array.isArray(body.detail)) {
        detail = body.detail.map((item) => item.msg || "Invalid input").join("; ");
      }
    } catch {
      // Keep the explicit HTTP status when the backend response is not JSON.
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export function getNpkConfig(): Promise<NpkConfig> {
  return request("/api/v1/config");
}

export function getNpkSensorDemo(): Promise<NpkSensorDemo> {
  return request("/api/v1/sensor-demo");
}

export function calculateNpkDose(
  calculation: NpkRequest
): Promise<NpkCalculationResponse> {
  return request("/api/v1/calculate", {
    method: "POST",
    body: JSON.stringify(calculation),
  });
}
