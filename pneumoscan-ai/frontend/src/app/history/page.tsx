"use client";

import Link from "next/link";
import Image from "next/image";
import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Loader2,
  RefreshCw,
  Trash2,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { usePredictionHistory } from "@/hooks/usePredictionHistory";
import { cn, formatDate, getPredictionColor } from "@/lib/utils";

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const { data, isLoading, error, refetch, deletePrediction } =
    usePredictionHistory(page, pageSize);

  const chartData = useMemo(
    () =>
      (data?.items ?? []).map((item) => ({
        id: item.id.slice(0, 8),
        confidence: Number(item.confidence_percentage.toFixed(1)),
        prediction: item.prediction,
      })),
    [data],
  );

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / pageSize));

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100">
      <header className="sticky top-0 z-40 border-b border-gray-800/50 bg-gray-950/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-400 transition-colors hover:bg-gray-800 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Link>
          <button
            onClick={refetch}
            disabled={isLoading}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-800 px-3 py-2 text-sm text-gray-200 transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
            Refresh
          </button>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-cyan-400">
              <Activity className="h-3.5 w-3.5" />
              Prediction History
            </p>
            <h1 className="text-3xl font-bold tracking-tight text-white">
              Stored X-ray Analyses
            </h1>
          </div>
          <p className="text-sm text-gray-500">
            {data?.total ?? 0} records in Supabase
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        <div className="mb-8 h-72 rounded-2xl border border-gray-800 bg-gray-900/50 p-4">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="id" stroke="#6b7280" tickLine={false} />
                <YAxis stroke="#6b7280" tickLine={false} domain={[0, 100]} />
                <Tooltip
                  cursor={{ fill: "rgba(8, 145, 178, 0.08)" }}
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #374151",
                    borderRadius: "0.75rem",
                  }}
                />
                <Bar dataKey="confidence" fill="#06b6d4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-gray-500">
              No history records to chart yet.
            </div>
          )}
        </div>

        <div className="overflow-hidden rounded-2xl border border-gray-800 bg-gray-900/50">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-3 text-gray-400">
              <Loader2 className="h-5 w-5 animate-spin" />
              Loading history
            </div>
          ) : data?.items.length ? (
            <div className="divide-y divide-gray-800">
              {data.items.map((item) => {
                const colors = getPredictionColor(item.prediction, item.severity);
                const isPneumonia = item.prediction === "PNEUMONIA";

                return (
                  <article
                    key={item.id}
                    className="grid gap-4 p-4 sm:grid-cols-[80px_1fr_auto] sm:items-center"
                  >
                    <div className="h-20 w-20 overflow-hidden rounded-xl border border-gray-800 bg-gray-950">
                      {item.image_url ? (
                        <Image
                          src={item.image_url}
                          alt="Chest X-ray"
                          width={80}
                          height={80}
                          unoptimized
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full items-center justify-center text-gray-700">
                          <Activity className="h-6 w-6" />
                        </div>
                      )}
                    </div>

                    <div className="min-w-0">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span
                          className={cn(
                            "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold",
                            colors.bg,
                            colors.border,
                            colors.text,
                          )}
                        >
                          {isPneumonia ? (
                            <AlertTriangle className="h-3.5 w-3.5" />
                          ) : (
                            <CheckCircle2 className="h-3.5 w-3.5" />
                          )}
                          {item.prediction}
                        </span>
                        <span className="text-xs text-gray-500">
                          {item.severity} risk
                        </span>
                      </div>
                      <p className="truncate font-mono text-xs text-gray-500">
                        {item.id}
                      </p>
                      <p className="mt-1 text-sm text-gray-400">
                        {formatDate(item.timestamp)} · {item.model_version}
                      </p>
                    </div>

                    <div className="flex items-center justify-between gap-4 sm:justify-end">
                      <div className="text-right">
                        <p className={cn("text-2xl font-bold", colors.text)}>
                          {item.confidence_percentage.toFixed(1)}%
                        </p>
                        <p className="text-xs text-gray-500">confidence</p>
                      </div>
                      <button
                        onClick={() => void deletePrediction(item.id)}
                        className="rounded-lg p-2 text-gray-500 transition-colors hover:bg-red-500/10 hover:text-red-400"
                        aria-label="Delete prediction"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center text-sm text-gray-500">
              No predictions have been saved yet.
            </div>
          )}
        </div>

        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={() => setPage((value) => Math.max(1, value - 1))}
            disabled={page <= 1}
            className="rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-200 transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Previous
          </button>
          <p className="text-sm text-gray-500">
            Page {page} of {totalPages}
          </p>
          <button
            onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
            disabled={page >= totalPages}
            className="rounded-lg bg-gray-800 px-4 py-2 text-sm text-gray-200 transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </section>
    </main>
  );
}
