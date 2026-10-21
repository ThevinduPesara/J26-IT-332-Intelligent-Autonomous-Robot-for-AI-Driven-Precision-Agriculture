"use client";

import React, { useState, useRef } from "react";
import {
  Upload,
  Image as ImageIcon,
  Video,
  RefreshCw,
  Sliders,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

export interface SampleMedia {
  label: string;
  type: "image" | "video";
  url: string;
}

interface ModelMediaUploaderProps {
  modelName: string;
  description: string;
  defaultSamples: SampleMedia[];
  isAnalyzing?: boolean;
  analyzedSuccess?: boolean;
  confidence?: number;
  onConfidenceChange?: (conf: number) => void;
  onAnalyze?: (media: {
    file: File | null;
    url: string;
    type: "image" | "video";
    name: string;
  }) => void;
}

export default function ModelMediaUploader({
  modelName,
  description,
  defaultSamples,
  isAnalyzing = false,
  analyzedSuccess = false,
  confidence = 0.25,
  onConfidenceChange,
  onAnalyze,
}: ModelMediaUploaderProps) {
  const [currentMedia, setCurrentMedia] = useState<{
    url: string;
    type: "image" | "video";
    name: string;
    file: File | null;
  }>(() => ({
    url: defaultSamples[0]?.url || "",
    type: defaultSamples[0]?.type || "image",
    name: defaultSamples[0]?.label || "Sample Media",
    file: null,
  }));

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle User File Upload (Photo or Video)
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const isVideo = file.type.startsWith("video/");
      const fileUrl = URL.createObjectURL(file);
      setCurrentMedia({
        url: fileUrl,
        type: isVideo ? "video" : "image",
        name: file.name,
        file: file,
      });
    }
  };

  const handleSelectSample = (sample: SampleMedia) => {
    setCurrentMedia({
      url: sample.url,
      type: sample.type,
      name: sample.label,
      file: null,
    });
  };

  const triggerAnalysis = () => {
    if (onAnalyze) {
      onAnalyze(currentMedia);
    }
  };

  return (
    <div className="bg-white rounded-3xl p-6 md:p-7 border border-slate-200/90 shadow-sm transition hover:shadow-md">
      {/* Title & Description */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5 pb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-800">
              Media Ingestion Pipeline
            </span>
          </div>
          <h3 className="text-base font-extrabold text-slate-800 flex items-center gap-2">
            <Upload className="w-4 h-4 text-emerald-700" />
            Input Feed for {modelName}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>

        {/* Preset Sample Selectors with enhanced visual focus */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Quick Samples:
          </span>
          {defaultSamples.map((sample) => {
            const isSelected = currentMedia.name === sample.label;
            return (
              <button
                key={sample.label}
                onClick={() => handleSelectSample(sample)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer flex items-center gap-1.5 shadow-2xs ${
                  isSelected
                    ? "bg-[#18533a] text-white shadow-sm ring-2 ring-emerald-600/30 scale-[1.02]"
                    : "bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-slate-900"
                }`}
              >
                {sample.type === "video" ? (
                  <Video className="w-3.5 h-3.5" />
                ) : (
                  <ImageIcon className="w-3.5 h-3.5" />
                )}
                <span>{sample.label}</span>
                {isSelected && <CheckCircle2 className="w-3 h-3 text-emerald-300" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Container: Left File Dropzone / Right Live Media Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        {/* Left: Upload Field & Threshold Controls */}
        <div className="flex flex-col gap-3.5">
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-200 hover:border-emerald-600 rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer bg-slate-50/70 hover:bg-emerald-50/30 transition-all duration-200 group flex-1 min-h-[190px]"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              className="hidden"
              onChange={handleFileUpload}
            />
            <div className="w-13 h-13 rounded-2xl bg-white group-hover:bg-emerald-600 group-hover:text-white shadow-xs border border-slate-200/80 flex items-center justify-center text-emerald-800 mb-3 transition-all duration-200 group-hover:scale-110">
              <Upload className="w-6 h-6" />
            </div>
            <span className="text-xs font-bold text-slate-800 group-hover:text-emerald-900">
              Drag & drop or Click to upload Leaf Image
            </span>
            <span className="text-[11px] text-slate-400 mt-1 max-w-xs">
              Direct high-resolution input for YOLO11s NPK defect classification
            </span>
            <span className="mt-3 px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-[11px] font-bold text-slate-700 shadow-2xs group-hover:border-emerald-400">
              Browse Files from Computer
            </span>
          </div>

          {/* Confidence Slider with Highlighted visual indicator */}
          {onConfidenceChange && (
            <div className="bg-slate-50 border border-slate-200/90 rounded-2xl p-3.5 flex items-center justify-between gap-4 shadow-2xs">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center">
                  <Sliders className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-800 block">
                    Deficiency Confidence Gate
                  </span>
                  <span className="text-[10px] text-slate-400">
                    Filter out background leaf reflections
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2.5">
                <input
                  type="range"
                  min="0.05"
                  max="1.0"
                  step="0.05"
                  value={confidence}
                  onChange={(e) => onConfidenceChange(parseFloat(e.target.value))}
                  className="w-28 accent-emerald-700 cursor-pointer"
                />
                <span className="font-mono text-xs font-black text-emerald-900 bg-white px-2 py-1 rounded-md border border-slate-200 shadow-2xs w-11 text-center">
                  {Math.round(confidence * 100)}%
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Right: Live Preview Box */}
        <div className="relative rounded-2xl overflow-hidden bg-slate-950 border border-slate-800 shadow-lg flex flex-col justify-between min-h-[220px]">
          {/* Media Player / Viewer */}
          {currentMedia.type === "video" ? (
            <video
              src={currentMedia.url}
              controls
              playsInline
              className="w-full h-full object-cover max-h-[280px]"
            />
          ) : (
            <div
              className="w-full h-full min-h-[220px] bg-contain bg-no-repeat bg-center transition-all duration-300"
              style={{ backgroundImage: `url('${currentMedia.url}')` }}
            />
          )}

          {/* Media Header Pill */}
          <div className="absolute top-3 left-3 bg-black/75 backdrop-blur-md px-3 py-1.5 rounded-xl text-[11px] font-mono font-bold text-white border border-white/10 flex items-center gap-2 shadow-md">
            {currentMedia.type === "video" ? (
              <Video className="w-3.5 h-3.5 text-teal-400" />
            ) : (
              <ImageIcon className="w-3.5 h-3.5 text-emerald-400" />
            )}
            <span className="truncate max-w-[220px]">{currentMedia.name}</span>
          </div>

          {/* Overlay Action Bar with High-Impact CTA button */}
          <div className="absolute bottom-3 inset-x-3 flex items-center justify-between gap-3 bg-slate-900/90 backdrop-blur-md p-2.5 rounded-2xl border border-white/15 shadow-xl">
            <div className="flex items-center gap-2 pl-2">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  analyzedSuccess
                    ? "bg-emerald-400"
                    : isAnalyzing
                    ? "bg-amber-400 animate-ping"
                    : "bg-emerald-400 animate-pulse"
                }`}
              />
              <span className="text-[11px] font-bold text-white/95">
                {isAnalyzing
                  ? "Evaluating leaf phenology..."
                  : analyzedSuccess
                  ? "Diagnosis Ready Below"
                  : "Ready for Deep Learning"}
              </span>
            </div>

            <button
              onClick={triggerAnalysis}
              disabled={isAnalyzing}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-black text-white bg-linear-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-md shadow-emerald-950/40 transition active:scale-95 cursor-pointer disabled:opacity-75"
            >
              <Sparkles
                className={`w-3.5 h-3.5 ${isAnalyzing ? "animate-spin" : ""}`}
              />
              {isAnalyzing ? "Processing..." : "Run AI Inference"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
