export interface PredictionResult {
  id: string;
  prediction: "PNEUMONIA" | "NORMAL";
  confidence: number;
  confidence_percentage: number;
  severity: "High" | "Medium" | "Low" | "Normal";
  image_url: string | null;
  heatmap_url: string | null;
  processing_time_ms: number;
  timestamp: string;
  model_version: string;
}

export interface PredictionHistoryItem {
  id: string;
  prediction: "PNEUMONIA" | "NORMAL";
  confidence: number;
  confidence_percentage: number;
  severity: "High" | "Medium" | "Low" | "Normal";
  image_url: string | null;
  heatmap_url: string | null;
  timestamp: string;
  model_version: string;
}

export interface PredictionHistoryResponse {
  items: PredictionHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface HealthStatus {
  status: string;
  model_loaded: boolean;
  environment: string;
  version: string;
  timestamp: string;
}

export type UploadState = 
  | "idle" 
  | "uploading" 
  | "processing" 
  | "success" 
  | "error";