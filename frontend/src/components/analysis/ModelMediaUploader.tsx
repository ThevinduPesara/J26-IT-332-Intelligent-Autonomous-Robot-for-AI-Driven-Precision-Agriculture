"use client";

import React, { useState, useRef } from "react";
import { Upload, Image as ImageIcon, Video, CheckCircle2, Play, RefreshCw, X } from "lucide-react";

interface SampleMedia {
  label: string;
  type: "image" | "video";
  url: string;
}

interface ModelMediaUploaderProps {
  modelName: string;
  description: string;
  defaultSamples: SampleMedia[];
  onAnalyze?: (fileUrl: string, type: "image" | "video") => void;
}

export default function ModelMediaUploader({
  modelName,
  description,
  defaultSamples,
  onAnalyze,
}: ModelMediaUploaderProps) {
  const [currentMedia, setCurrentMedia] = useState<{
    url: string;
    type: "image" | "video";
    name: string;
  }>(() => ({
    url: defaultSamples[0]?.url || "",
    type: defaultSamples[0]?.type || "image",
    name: defaultSamples[0]?.label || "Sample Media",
  }));

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzedSuccess, setAnalyzedSuccess] = useState(false);
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
      });
      setAnalyzedSuccess(false);
    }
  };

  const handleSelectSample = (sample: SampleMedia) => {
    setCurrentMedia({
      url: sample.url,
      type: sample.type,
      name: sample.label,
    });
    setAnalyzedSuccess(false);
  };

  const triggerAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      setAnalyzedSuccess(true);
      if (onAnalyze) {
        onAnalyze(currentMedia.url, currentMedia.type);
      }
    }, 1200);
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
      {/* Title & Description */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
            <Upload className="w-4 h-4 text-emerald-700" />
            Media Input for {modelName} (Photo & Video)
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>

        {/* Preset Sample Selectors */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[11px] font-semibold text-slate-400">
            Presets:
          </span>
          {defaultSamples.map((sample) => (
            <button
              key={sample.label}
              onClick={() => handleSelectSample(sample)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-1.5 ${
                currentMedia.name === sample.label
                  ? "bg-[#18533a] text-white shadow-xs"
                  : "bg-slate-100 hover:bg-slate-200 text-slate-700"
              }`}
            >
              {sample.type === "video" ? (
                <Video className="w-3.5 h-3.5" />
              ) : (
                <ImageIcon className="w-3.5 h-3.5" />
              )}
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Container: Left File Dropzone / Right Live Media Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-stretch">
        {/* Left: Upload Field */}
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-slate-200 hover:border-emerald-600 rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer bg-slate-50/50 hover:bg-emerald-50/20 transition group min-h-[220px]"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,video/*"
            className="hidden"
            onChange={handleFileUpload}
          />
          <div className="w-12 h-12 rounded-2xl bg-white group-hover:bg-emerald-100/60 shadow-xs border border-slate-200/80 flex items-center justify-center text-emerald-800 mb-3 transition">
            <Upload className="w-6 h-6" />
          </div>
          <span className="text-xs font-bold text-slate-800">
            Click to upload Photo or Video
          </span>
          <span className="text-[11px] text-slate-400 mt-1 max-w-xs">
            Supports JPG, PNG, WebP, MP4, WebM (Drone footage, field cameras)
          </span>
          <span className="mt-3 px-3 py-1 rounded-md bg-white border border-slate-200 text-[11px] font-semibold text-slate-700 shadow-2xs">
            Browse Local File
          </span>
        </div>

        {/* Right: Live Preview Box */}
        <div className="relative rounded-xl overflow-hidden bg-slate-900 border border-slate-200 shadow-inner flex flex-col justify-between min-h-[220px]">
          {/* Media Player / Viewer */}
          {currentMedia.type === "video" ? (
            <video
              src={currentMedia.url}
              controls
              playsInline
              className="w-full h-full object-cover max-h-[260px]"
            />
          ) : (
            <div
              className="w-full h-full min-h-[200px] bg-cover bg-center transition-transform duration-500"
              style={{ backgroundImage: `url('${currentMedia.url}')` }}
            />
          )}

          {/* Media Header Pill */}
          <div className="absolute top-2.5 left-2.5 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-mono text-white/90 border border-white/10 flex items-center gap-1.5">
            {currentMedia.type === "video" ? (
              <Video className="w-3.5 h-3.5 text-teal-400" />
            ) : (
              <ImageIcon className="w-3.5 h-3.5 text-emerald-400" />
            )}
            <span>{currentMedia.name}</span>
          </div>

          {/* Overlay Status or Action Trigger */}
          <div className="absolute bottom-2.5 inset-x-2.5 flex items-center justify-between gap-2 bg-black/60 backdrop-blur-md p-2 rounded-xl border border-white/10">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[11px] font-semibold text-white/90">
                {analyzedSuccess ? "Inference Complete" : "Ready for AI Pipeline"}
              </span>
            </div>

            <button
              onClick={triggerAnalysis}
              disabled={isAnalyzing}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-[#0f5132] hover:bg-emerald-900 transition active:scale-95 cursor-pointer disabled:opacity-75"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${isAnalyzing ? "animate-spin" : ""}`}
              />
              {isAnalyzing ? "Analyzing..." : "Run AI Inference"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
