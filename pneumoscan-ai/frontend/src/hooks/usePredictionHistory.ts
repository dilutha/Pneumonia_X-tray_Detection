"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { PredictionHistoryResponse } from "@/types/prediction";

interface UseHistoryResult {
  data: PredictionHistoryResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
  deletePrediction: (id: string) => Promise<void>;
}

export function usePredictionHistory(
  page: number = 1,
  pageSize: number = 10,
): UseHistoryResult {
  const [data, setData] = useState<PredictionHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async (signal?: AbortSignal) => {
    setIsLoading(true);
    setError(null);
    try {
      if (signal?.aborted) return;
      const result = await api.getHistory(page, pageSize);
      if (signal?.aborted) return;
      setData(result);
    } catch (err) {
      if (signal?.aborted) return;
      setError("Failed to load prediction history");
      console.error(err);
    } finally {
      if (!signal?.aborted) {
        setIsLoading(false);
      }
    }
  }, [page, pageSize]);

  useEffect(() => {
    const controller = new AbortController();

    async function loadHistory() {
      await fetchHistory(controller.signal);
    }

    void loadHistory();

    return () => controller.abort();
  }, [fetchHistory]);

  const deletePrediction = async (id: string) => {
    try {
      await api.deletePrediction(id);
      // Optimistic update — remove from local state immediately
      setData((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.filter((item) => item.id !== id),
              total: prev.total - 1,
            }
          : null,
      );
    } catch {
      setError("Failed to delete prediction");
    }
  };

  return { data, isLoading, error, refetch: fetchHistory, deletePrediction };
}
