export interface PaddyModel {
  id: string;
  name: string;
  family: string;
  badge: string;
  note: string;
  available: boolean;
  size_mb: number | null;
}

export interface PaddyModelsResponse {
  models: PaddyModel[];
  labels: string[];
  ensemble_ready: boolean;
}

export interface PaddyClassStat {
  id: number;
  name: string;
  color: string;
  percent: number;
  pixels: number;
  mean_confidence: number | null;
}

export interface PaddyPredictionResponse {
  width: number;
  height: number;
  stats: PaddyClassStat[];
  mean_confidence: number;
  images: {
    original_png: string;
    overlay_png: string;
    mask_png: string;
    confidence_png: string;
  };
  model_id: string;
  model_name: string;
  contributors: string[];
  inference_seconds: number;
  checkpoint_epoch?: number | null;
  checkpoint_val_miou?: number | null;
  device: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_PADDY_API_URL || "http://127.0.0.1:8003";

async function throwApiError(response: Response): Promise<never> {
  let message = `PaddyVision request failed (${response.status})`;
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      message = body.detail;
    } else if (body.detail) {
      message = JSON.stringify(body.detail);
    }
  } catch {
    // Keep the HTTP status message when the response is not JSON.
  }
  throw new Error(message);
}

export async function checkPaddyApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      cache: "no-store",
    });
    if (!response.ok) return false;
    const body = (await response.json()) as { status?: string };
    return body.status === "ok";
  } catch {
    return false;
  }
}

export async function getPaddyModels(): Promise<PaddyModelsResponse> {
  const response = await fetch(`${API_BASE_URL}/models`, {
    cache: "no-store",
  });
  if (!response.ok) return throwApiError(response);
  return (await response.json()) as PaddyModelsResponse;
}

export async function predictPaddyImage(
  file: File,
  modelId: string,
  alpha: number,
): Promise<PaddyPredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("model_id", modelId);
  formData.append("alpha", String(alpha));

  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) return throwApiError(response);
  return (await response.json()) as PaddyPredictionResponse;
}