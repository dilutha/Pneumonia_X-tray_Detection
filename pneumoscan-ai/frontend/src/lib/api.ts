/**
 * api.ts — Centralized API client for all backend calls.
 * 
 * Why centralize API calls?
 *   - One place to change the base URL
 *   - Consistent error handling
 *   - Easy to add auth headers later
 *   - TypeScript types enforced at the boundary
 */

import { PredictionResult, PredictionHistoryResponse, HealthStatus } from "@/types/prediction";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = "";
    try {
      const errorData = await response.json();
      detail = errorData.detail || errorData.error || "";
    } catch {
      detail = response.statusText;
    }
    throw new APIError(
      `API Error ${response.status}: ${detail}`,
      response.status,
      detail,
    );
  }
  return response.json() as Promise<T>;
}

export const api = {
  /**
   * Uploads a chest X-ray and returns the prediction result.
   * Uses FormData (multipart/form-data) as required by FastAPI's File parameter.
   */
  predict: async (
    file: File,
    onProgress?: (progress: number) => void,
  ): Promise<PredictionResult> => {
    const formData = new FormData();
    formData.append("file", file);

    // Using XMLHttpRequest for progress events (fetch doesn't support upload progress)
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable && onProgress) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      });
      
      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new APIError(error.detail || "Prediction failed", xhr.status));
          } catch {
            reject(new APIError("Prediction failed", xhr.status));
          }
        }
      });
      
      xhr.addEventListener("error", () => {
        reject(new APIError("Network error — is the backend running?", 0));
      });
      
      xhr.open("POST", "/api/predict");
      xhr.send(formData);
    });
  },

  /**
   * Fetches paginated prediction history.
   */
  getHistory: async (
    page: number = 1,
    pageSize: number = 10,
  ): Promise<PredictionHistoryResponse> => {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/history?page=${page}&page_size=${pageSize}`,
    );
    return handleResponse<PredictionHistoryResponse>(response);
  },

  /**
   * Deletes a prediction record.
   */
  deletePrediction: async (id: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new APIError("Failed to delete prediction", response.status);
    }
  },

  /**
   * Checks if the backend API and model are healthy.
   */
  healthCheck: async (): Promise<HealthStatus> => {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
      next: { revalidate: 30 }, // Cache for 30 seconds in Next.js
    });
    return handleResponse<HealthStatus>(response);
  },
};

export { APIError };