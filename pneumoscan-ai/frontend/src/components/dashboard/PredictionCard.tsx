"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Zap,
  Eye,
  Brain,
  Activity,
} from "lucide-react";
import { PredictionResult } from "@/types/prediction";
import { cn, getPredictionColor, formatDate } from "@/lib/utils";

interface PredictionCardProps {
  result: PredictionResult;
}

export function PredictionCard({ result }: PredictionCardProps) {
  const colors = getPredictionColor(result.prediction, result.severity);
  const isPneumonia = result.prediction === "PNEUMONIA";

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, type: "spring", stiffness: 200 }}
      className="glass-card rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <div
        className={cn(
          "px-6 py-5 border-b border-gray-800/50 flex items-center gap-4",
          colors.bg,
        )}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 300 }}
          className={cn(
            "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0",
            colors.bg,
            colors.border,
            "border",
          )}
        >
          {isPneumonia ? (
            <AlertTriangle className={cn("w-6 h-6", colors.text)} />
          ) : (
            <CheckCircle2 className={cn("w-6 h-6", colors.text)} />
          )}
        </motion.div>
        
        <div>
          <motion.p
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            Diagnosis Result
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className={cn("text-2xl font-bold tracking-tight", colors.text)}
          >
            {result.prediction}
          </motion.h2>
        </div>

        {result.severity !== "Normal" && (
          <motion.span
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className={cn(
              "ml-auto px-3 py-1 rounded-full text-xs font-semibold border",
              colors.bg,
              colors.text,
              colors.border,
            )}
          >
            {result.severity} Risk
          </motion.span>
        )}
      </div>

      {/* Confidence Score */}
      <div className="px-6 py-5 border-b border-gray-800/50">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Activity className="w-4 h-4" />
            Confidence Score
          </div>
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className={cn("text-2xl font-bold font-mono", colors.text)}
          >
            {result.confidence_percentage.toFixed(1)}%
          </motion.span>
        </div>
        
        {/* Animated progress bar */}
        <div className="h-2.5 bg-gray-800 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${result.confidence_percentage}%` }}
            transition={{ delay: 0.7, duration: 0.8, ease: "easeOut" }}
            className={cn(
              "h-full rounded-full",
              isPneumonia
                ? result.severity === "High"
                  ? "bg-gradient-to-r from-red-500 to-red-400"
                  : result.severity === "Medium"
                  ? "bg-gradient-to-r from-amber-500 to-amber-400"
                  : "bg-gradient-to-r from-orange-500 to-orange-400"
                : "bg-gradient-to-r from-emerald-500 to-emerald-400",
            )}
          />
        </div>
        
        <div className="flex justify-between mt-2 text-xs text-gray-600">
          <span>0%</span>
          <span>Threshold: 50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Images: X-ray + Heatmap */}
      {(result.image_url || result.heatmap_url) && (
        <div className="px-6 py-5 border-b border-gray-800/50">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Eye className="w-3 h-3" />
            Visual Analysis
          </p>
          <div className="grid grid-cols-2 gap-3">
            {result.image_url && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 }}
                className="space-y-2"
              >
                <p className="text-xs text-gray-500 text-center">Original X-Ray</p>
                <Image
                  src={result.image_url}
                  alt="Chest X-Ray"
                  width={320}
                  height={320}
                  unoptimized
                  className="w-full aspect-square object-cover rounded-xl border border-gray-700"
                />
              </motion.div>
            )}
            {result.heatmap_url && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.9 }}
                className="space-y-2"
              >
                <p className="text-xs text-gray-500 text-center">
                  Grad-CAM Heatmap
                </p>
                <div className="relative">
                  <Image
                    src={result.heatmap_url}
                    alt="Grad-CAM Heatmap"
                    width={320}
                    height={320}
                    unoptimized
                    className="w-full aspect-square object-cover rounded-xl border border-gray-700"
                  />
                  <div className="absolute top-2 right-2 flex gap-1">
                    {["blue", "green", "red"].map((color, i) => (
                      <div
                        key={color}
                        className={cn(
                          "w-2 h-2 rounded-full",
                          i === 0 && "bg-blue-500",
                          i === 1 && "bg-green-500",
                          i === 2 && "bg-red-500",
                        )}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-xs text-gray-600 text-center">Red = high attention</p>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="px-6 py-4 grid grid-cols-3 gap-4">
        {[
          {
            icon: Brain,
            label: "Model",
            value: result.model_version,
          },
          {
            icon: Zap,
            label: "Speed",
            value: `${result.processing_time_ms.toFixed(0)}ms`,
          },
          {
            icon: Clock,
            label: "Time",
            value: formatDate(result.timestamp).split(",")[0],
          },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 + i * 0.1 }}
            className="flex flex-col items-center gap-1"
          >
            <item.icon className="w-4 h-4 text-gray-500" />
            <p className="text-[10px] text-gray-600 uppercase tracking-wider">
              {item.label}
            </p>
            <p className="text-sm font-mono text-gray-300">{item.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Medical Disclaimer */}
      <div className="px-6 py-3 bg-amber-500/5 border-t border-amber-500/10">
        <p className="text-xs text-amber-400/70 text-center">
          ⚕ This AI analysis is for research purposes only. Always consult a qualified radiologist.
        </p>
      </div>
    </motion.div>
  );
}
