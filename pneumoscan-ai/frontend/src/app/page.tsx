"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Stethoscope,
  Loader2,
  AlertCircle,
  History,
  GitBranch,
} from "lucide-react";
import Link from "next/link";

import { UploadZone } from "@/components/dashboard/UploadZone";
import { PredictionCard } from "@/components/dashboard/PredictionCard";
import { api, APIError } from "@/lib/api";
import { PredictionResult, UploadState } from "@/types/prediction";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((file: File | null) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
    setUploadState("idle");
  }, []);

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setUploadState("uploading");
    setError(null);
    setResult(null);
    setUploadProgress(0);

    try {
      // Upload + inference
      const prediction = await api.predict(selectedFile, (progress) => {
        setUploadProgress(progress);
        if (progress === 100) setUploadState("processing");
      });

      setResult(prediction);
      setUploadState("success");
    } catch (err) {
      setUploadState("error");
      if (err instanceof APIError) {
        setError(err.detail || err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    }
  };

  const isLoading =
    uploadState === "uploading" || uploadState === "processing";

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Background grid */}
      <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center opacity-[0.02] pointer-events-none" />

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-gray-800/50 bg-gray-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <Stethoscope className="w-4 h-4 text-white" />
              </div>
              <div>
                <span className="font-bold text-white tracking-tight">PneumoScan</span>
                <span className="gradient-text font-bold tracking-tight"> AI</span>
              </div>
            </div>

            <nav className="flex items-center gap-4">
              <Link
                href="/history"
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-800"
              >
                <History className="w-4 h-4" />
                History
              </Link>
              <a
                href="https://github.com/your-username/pneumoscan-ai"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-gray-800"
              >
                <GitBranch className="w-4 h-4" />
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-xs text-cyan-400 mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            CNN Model · TensorFlow · Grad-CAM
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
            Pneumonia Detection{" "}
            <span className="gradient-text">from X-Rays</span>
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Upload a chest X-ray image and our deep learning model will analyze
            it for pneumonia indicators, with visual explanations via Grad-CAM
            heatmaps.
          </p>
        </motion.div>

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Left: Upload + Analyze */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-4"
          >
            <UploadZone
              onFileSelect={handleFileSelect}
              isLoading={isLoading}
            />

            {/* Analyze button */}
            <motion.button
              onClick={handleAnalyze}
              disabled={!selectedFile || isLoading}
              whileHover={{ scale: selectedFile && !isLoading ? 1.02 : 1 }}
              whileTap={{ scale: selectedFile && !isLoading ? 0.98 : 1 }}
              className={cn(
                "w-full py-4 rounded-xl font-semibold text-white transition-all duration-200 flex items-center justify-center gap-3",
                selectedFile && !isLoading
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 shadow-lg shadow-cyan-500/25"
                  : "bg-gray-800 text-gray-500 cursor-not-allowed",
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {uploadState === "uploading"
                    ? `Uploading... ${uploadProgress}%`
                    : "Analyzing with AI..."}
                </>
              ) : (
                <>
                  <Stethoscope className="w-5 h-5" />
                  Analyze X-Ray
                </>
              )}
            </motion.button>

            {/* Processing steps indicator */}
            <AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="glass-card rounded-xl p-4 space-y-2"
                >
                  {[
                    {
                      label: "Uploading image",
                      done: uploadState === "processing",
                    },
                    {
                      label: "Preprocessing (resize, normalize)",
                      done: false,
                    },
                    { label: "CNN inference", done: false },
                    {
                      label: "Generating Grad-CAM heatmap",
                      done: false,
                    },
                    {
                      label: "Saving to database",
                      done: false,
                    },
                  ].map((step) => (
                    <div key={step.label} className="flex items-center gap-3">
                      <div
                        className={cn(
                          "w-1.5 h-1.5 rounded-full flex-shrink-0",
                          step.done
                            ? "bg-emerald-400"
                            : "bg-cyan-400 animate-pulse",
                        )}
                      />
                      <span
                        className={cn(
                          "text-sm",
                          step.done ? "text-gray-400" : "text-gray-300",
                        )}
                      >
                        {step.label}
                      </span>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error state */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400"
                >
                  <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">Analysis failed</p>
                    <p className="text-xs text-red-400/70 mt-0.5">{error}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Right: Result or placeholder */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <AnimatePresence mode="wait">
              {result ? (
                <PredictionCard key="result" result={result} />
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="glass-card rounded-2xl p-8 flex flex-col items-center justify-center text-center h-64"
                >
                  <div className="w-16 h-16 rounded-2xl bg-gray-800 flex items-center justify-center mb-4">
                    <Stethoscope className="w-8 h-8 text-gray-600" />
                  </div>
                  <p className="text-gray-500 text-sm">
                    Upload a chest X-ray and click Analyze to see the AI prediction
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-12"
        >
          {[
            { label: "Model Architecture", value: "CNN" },
            { label: "Training Dataset", value: "Chest X-Ray" },
            { label: "Explainability", value: "Grad-CAM" },
            { label: "Inference Time", value: "~100ms" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="glass-card rounded-xl p-4 text-center"
            >
              <p className="gradient-text text-lg font-bold">{stat.value}</p>
              <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </main>
    </div>
  );
}
