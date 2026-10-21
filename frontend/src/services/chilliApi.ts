export interface BoundingBox {
  x1: float;
  y1: float;
  x2: float;
  y2: float;
}

export type float = number;

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bounding_box: BoundingBox;
}

export interface ClassSummaryItem {
  detections: number;
  average_confidence: number;
  highest_confidence: number;
  vote_score: number;
}

export interface PredictionResponse {
  request_id: string;
  overall_prediction: "Healthy" | "N_Def" | "P_Def" | "K_Def" | string;
  overall_confidence: number;
  number_of_detections: number;
  detections: Detection[];
  class_summary: Record<string, ClassSummaryItem>;
  original_image_url: string;
  annotated_image_url: string;
  result_json_url: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_CHILLI_API_URL || "http://127.0.0.1:8000";

/**
 * Returns full URL for an image endpoint (handling relative URLs from backend)
 */
export function getChilliAssetUrl(relativeOrAbsoluteUrl: string): string {
  if (!relativeOrAbsoluteUrl) return "";
  if (
    relativeOrAbsoluteUrl.startsWith("http://") ||
    relativeOrAbsoluteUrl.startsWith("https://") ||
    relativeOrAbsoluteUrl.startsWith("blob:") ||
    relativeOrAbsoluteUrl.startsWith("data:")
  ) {
    return relativeOrAbsoluteUrl;
  }
  const cleanBase = API_BASE_URL.replace(/\/+$/, "");
  const cleanPath = relativeOrAbsoluteUrl.startsWith("/")
    ? relativeOrAbsoluteUrl
    : `/${relativeOrAbsoluteUrl}`;
  return `${cleanBase}${cleanPath}`;
}

/**
 * Check backend health status
 */
export async function checkChilliApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
      cache: "no-store",
    });
    if (!res.ok) return false;
    const data = await res.json();
    return data.status === "healthy" && data.model_loaded === true;
  } catch {
    return false;
  }
}

/**
 * Run inference on a chilli plant image
 */
export async function predictChilliImage(
  file: File,
  confidence: number = 0.25
): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_BASE_URL}/predict/image?confidence=${confidence}`;
  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = "Failed to run model inference";
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorDetail =
          typeof errJson.detail === "string"
            ? errJson.detail
            : JSON.stringify(errJson.detail);
      }
    } catch {
      // Fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}
