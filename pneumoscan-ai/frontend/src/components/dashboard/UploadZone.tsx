"use client";

import { useCallback, useState } from "react";
import Image from "next/image";
import { FileRejection, useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, X, FileImage, AlertCircle, CheckCircle2 } from "lucide-react";
import { cn, formatFileSize } from "@/lib/utils";

interface UploadZoneProps {
  onFileSelect: (file: File | null) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const ACCEPTED_TYPES = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
};

export function UploadZone({ onFileSelect, isLoading, disabled }: UploadZoneProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      setError(null);

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === "file-too-large") {
          setError("File too large. Maximum size is 10MB.");
        } else if (rejection.errors[0]?.code === "file-invalid-type") {
          setError("Invalid file type. Please upload a JPEG, PNG, or WebP image.");
        } else {
          setError("Invalid file. Please try again.");
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        setSelectedFile(file);
        
        // Create preview URL
        const url = URL.createObjectURL(file);
        setPreview(url);
        
        onFileSelect(file);
      }
    },
    [onFileSelect],
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    disabled: isLoading || disabled,
  });

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    setSelectedFile(null);
    setError(null);
    onFileSelect(null);
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          "relative rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer overflow-hidden",
          isDragActive && !isDragReject && "border-cyan-400 bg-cyan-400/5 scale-[1.02]",
          isDragReject && "border-red-400 bg-red-400/5",
          !isDragActive && !preview && "border-gray-700 bg-gray-900/50 hover:border-gray-600 hover:bg-gray-900/80",
          preview && "border-gray-700 bg-gray-900",
          (isLoading || disabled) && "cursor-not-allowed opacity-60",
        )}
      >
        <input {...getInputProps()} />

        {/* Background pulse animation when dragging */}
        <AnimatePresence>
          {isDragActive && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-blue-500/5"
            />
          )}
        </AnimatePresence>

        {/* Content */}
        <div className="p-8">
          {preview && selectedFile ? (
            /* File selected state */
            <div className="flex items-center gap-6">
              {/* Thumbnail */}
              <div className="relative flex-shrink-0">
                <Image
                  src={preview}
                  alt="X-ray preview"
                  width={96}
                  height={96}
                  unoptimized
                  className="w-24 h-24 object-cover rounded-xl border border-gray-700"
                />
                <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
                  <CheckCircle2 className="w-3 h-3 text-white" />
                </div>
              </div>
              
              {/* File info */}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-200 truncate">{selectedFile.name}</p>
                <p className="text-sm text-gray-500 mt-1">
                  {formatFileSize(selectedFile.size)} · {selectedFile.type}
                </p>
                <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  Ready for analysis
                </p>
              </div>
              
              {/* Remove button */}
              {!isLoading && (
                <button
                  onClick={clearFile}
                  className="flex-shrink-0 p-2 rounded-lg bg-gray-800 hover:bg-red-500/20 hover:text-red-400 text-gray-400 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          ) : (
            /* Empty state */
            <div className="flex flex-col items-center justify-center py-6 text-center">
              <motion.div
                animate={isDragActive ? { scale: 1.2, rotate: 5 } : { scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 300 }}
                className={cn(
                  "w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-colors",
                  isDragActive
                    ? "bg-cyan-400/20 text-cyan-400"
                    : "bg-gray-800 text-gray-400",
                )}
              >
                {isDragActive ? (
                  <FileImage className="w-8 h-8" />
                ) : (
                  <Upload className="w-8 h-8" />
                )}
              </motion.div>
              
              <p className="text-lg font-medium text-gray-200 mb-1">
                {isDragActive ? "Drop to analyze" : "Upload Chest X-Ray"}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Drag & drop or click to browse
              </p>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <span className="px-2 py-1 rounded bg-gray-800 border border-gray-700">JPEG</span>
                <span className="px-2 py-1 rounded bg-gray-800 border border-gray-700">PNG</span>
                <span className="px-2 py-1 rounded bg-gray-800 border border-gray-700">WebP</span>
                <span className="text-gray-700">·</span>
                <span>Max 10MB</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-3 flex items-center gap-2 text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-xl px-4 py-3"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
