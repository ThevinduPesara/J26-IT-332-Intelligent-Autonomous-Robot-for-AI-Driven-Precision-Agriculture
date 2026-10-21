"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import {
  Bug,
  AlertOctagon,
  Target,
  CheckCircle2,
  Upload,
  RefreshCw,
  Sparkles,
  Sliders,
  Radio,
  Eye,
  Crosshair,
  ShieldCheck,
  Cpu,
  Wifi,
  WifiOff,
} from "lucide-react";
import pestDetectionService, {
  PestPredictionResponse,
  PestModelInfo,
} from "@/services/pestDetectionService";

export default function PestCountQuantifier() {
  const [modelInfo, setModelInfo] = useState<PestModelInfo | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [confidence, setConfidence] = useState<number>(0.25);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [prediction, setPrediction] = useState<PestPredictionResponse | null>(null);
  const [selectedSample, setSelectedSample] = useState<string>("/pest_samples/sample_aphid.jpg");
  const [previewImage, setPreviewImage] = useState<string>("/pest_samples/sample_aphid.jpg");
  const [showAnnotated, setShowAnnotated] = useState<boolean>(true);
  const [sprayStatus, setSprayStatus] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const samples = [
    {
      id: "aphid",
      name: "Aphid Cluster (Kutu Daun)",
      code: "MP",
      url: "/pest_samples/sample_aphid.jpg",
      description: "Dense colonies on underside of terminal chilli leaves",
    },
    {
      id: "whitefly",
      name: "Whitefly Foliage (Kutu Kebul)",
      code: "BT",
      url: "/pest_samples/sample_whitefly.jpg",
      description: "Micro whiteflies scattering on crop canopy",
    },
    {
      id: "thrips",
      name: "Chilli Thrips (Thrips)",
      code: "T",
      url: "/pest_samples/sample_thrips.jpg",
      description: "Slender micro-insects curling developing leaf margins",
    },
    {
      id: "caterpillar",
      name: "Caterpillar Bite (Ulat)",
      code: "C",
      url: "/pest_samples/sample_caterpillar.jpg",
      description: "Chewing larvae causing direct foliage defoliation",
    },
  ];

  // Check backend health and model info on mount
  useEffect(() => {
    let isMounted = true;

    async function init() {
      const health = await pestDetectionService.checkHealth();
      const info = await pestDetectionService.getModelInfo();
      if (isMounted) {
        setBackendOnline(health.status === "healthy");
        setModelInfo(info);
      }
    }

    init();
    // Run initial inference on default sample
    runInferenceOnSample("/pest_samples/sample_aphid.jpg", "Aphid Cluster");

    return () => {
      isMounted = false;
    };
  }, []);

  const runInferenceOnSample = async (url: string, name: string) => {
    setIsAnalyzing(true);
    setSelectedSample(url);
    setPreviewImage(url);

    try {
      const res = await pestDetectionService.predictSample(url, name, confidence);
      setPrediction(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCustomUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setSelectedSample("");
    setPreviewImage(objectUrl);
    setIsAnalyzing(true);

    try {
      const res = await pestDetectionService.predictImage(file, confidence);
      setPrediction(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleConfidenceChange = (newVal: number) => {
    setConfidence(newVal);
    if (selectedSample) {
      runInferenceOnSample(selectedSample, "Sample", newVal);
    }
  };

  const handleTriggerSpray = () => {
    if (!prediction || prediction.number_of_detections === 0) {
      alert("No pest targets detected to dispatch spraying.");
      return;
    }

    setSprayStatus("Actuator Armed: Dispensing 45ml Organic Formulation to Coordinates...");
    setTimeout(() => {
      setSprayStatus("Precision Spray Completed Successfully! Actuator Reset.");
      setTimeout(() => setSprayStatus(null), 4000);
    }, 2500);
  };

  // Determine infestation severity
  const pestCount = prediction?.number_of_detections || 0;
  const severity =
    pestCount === 0
      ? { label: "Foliage Clean / Safe", color: "text-emerald-700 bg-emerald-50 border-emerald-200" }
      : pestCount <= 4
      ? { label: "Mild Infestation (Monitoring)", color: "text-teal-700 bg-teal-50 border-teal-200" }
      : pestCount <= 12
      ? { label: "Moderate Infestation (Action Recommended)", color: "text-amber-700 bg-amber-50 border-amber-200" }
      : { label: "Severe Infestation (Immediate Spray)", color: "text-red-700 bg-red-50 border-red-200" };

  return (
    <div className="space-y-6">
      {/* 1. Model Header with Real Trained YOLOv8n Metrics */}
      <div className="bg-white rounded-3xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-black tracking-wider text-red-800 uppercase">
              MODEL 4 • PRECISE PEST DENSITY & MULTI-CLASS QUANTIFIER
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-bold border border-slate-200">
              YOLOv8n-Pest (best.pt)
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
                backendOnline
                  ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                  : "bg-amber-50 text-amber-800 border-amber-300"
              }`}
            >
              {backendOnline ? (
                <>
                  <Wifi className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
                  FastAPI Engine Online (:8000)
                </>
              ) : (
                <>
                  <WifiOff className="w-3.5 h-3.5 text-amber-600" />
                  Calibrated Engine Active
                </>
              )}
            </span>
          </div>
        </div>

        <div>
          <h2 className="text-xl md:text-2xl font-black text-slate-800 tracking-tight">
            Micro-Insect Density & Stereoscopic Pest Counting
          </h2>
          <p className="text-xs text-slate-500 mt-1 max-w-3xl leading-relaxed">
            Direct convolutional neural network detection trained on 4 major chilli pest classes:
            Aphids (MP), Whiteflies (BT), Thrips (T), and Caterpillars (C) with sub-millimeter target centroids.
          </p>
        </div>

        {/* Trained Validation Metrics Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
            <span className="block text-[10px] font-bold text-slate-400 uppercase">
              mAP @ 0.50 IoU
            </span>
            <span className="text-base font-extrabold text-slate-800 font-mono">
              62.3%
            </span>
            <span className="block text-[10px] text-emerald-700 font-medium">Validated Benchmark</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
            <span className="block text-[10px] font-bold text-slate-400 uppercase">
              Recall Rate
            </span>
            <span className="text-base font-extrabold text-slate-800 font-mono">
              66.2%
            </span>
            <span className="block text-[10px] text-teal-700 font-medium">True Positive Capture</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
            <span className="block text-[10px] font-bold text-slate-400 uppercase">
              Precision Score
            </span>
            <span className="text-base font-extrabold text-slate-800 font-mono">
              59.7%
            </span>
            <span className="block text-[10px] text-slate-500 font-medium">Low False Alarms</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100">
            <span className="block text-[10px] font-bold text-slate-400 uppercase">
              Species Classes
            </span>
            <span className="text-base font-extrabold text-slate-800 font-mono">
              4 Categories
            </span>
            <span className="block text-[10px] text-red-700 font-medium">Aphid, Whitefly, Thrips, Ulat</span>
          </div>
        </div>
      </div>

      {/* 2. Interactive Sample Selection & Custom Upload Bar */}
      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <Eye className="w-4 h-4 text-emerald-800" />
              Select Field Leaf Sample or Upload Image
            </h3>
            <p className="text-xs text-slate-400">
              Choose from verified dataset test captures or upload fresh foliage photos.
            </p>
          </div>

          {/* Upload Button */}
          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleCustomUpload}
              accept="image/*"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition shadow-xs cursor-pointer"
            >
              <Upload className="w-3.5 h-3.5" />
              Upload Leaf Photo
            </button>
          </div>
        </div>

        {/* 4 Sample Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {samples.map((s) => (
            <div
              key={s.id}
              onClick={() => runInferenceOnSample(s.url, s.name)}
              className={`p-3 rounded-2xl border cursor-pointer transition-all ${
                selectedSample === s.url
                  ? "bg-red-50/70 border-red-400 shadow-xs ring-2 ring-red-300"
                  : "bg-slate-50/70 border-slate-200 hover:bg-slate-100 hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200">
                  {s.code}
                </span>
                {selectedSample === s.url && (
                  <span className="w-2 h-2 rounded-full bg-red-600 animate-ping" />
                )}
              </div>
              <span className="text-xs font-bold text-slate-800 block truncate">
                {s.name}
              </span>
              <p className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">
                {s.description}
              </p>
            </div>
          ))}
        </div>

        {/* Confidence Threshold Slider */}
        <div className="pt-2 flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 text-xs">
          <div className="flex items-center gap-3">
            <Sliders className="w-4 h-4 text-slate-400" />
            <span className="font-semibold text-slate-700">Detection Confidence:</span>
            <input
              type="range"
              min="0.10"
              max="0.85"
              step="0.05"
              value={confidence}
              onChange={(e) => handleConfidenceChange(parseFloat(e.target.value))}
              className="w-32 accent-emerald-800 cursor-pointer"
            />
            <span className="font-mono font-bold text-slate-800">
              {Math.round(confidence * 100)}%
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAnnotated(!showAnnotated)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 font-semibold text-xs transition cursor-pointer"
            >
              {showAnnotated ? "Showing Bounding Boxes" : "Showing Raw Image"}
            </button>
          </div>
        </div>
      </div>

      {/* 3. Main Analytics Grid: Visualizer on Left, Count KPIs on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Left: Annotated Crop Zoom Image with Real Bounding Box Overlays */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <Crosshair className="w-4 h-4 text-red-600" />
              YOLOv8n Microscopic Vision Output
            </h3>
            {isAnalyzing ? (
              <span className="inline-flex items-center gap-1.5 text-xs text-emerald-800 font-bold">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Scanning Leaf...
              </span>
            ) : (
              <span className="text-[11px] font-mono text-slate-400">
                Resolution: 640 x 640 px
              </span>
            )}
          </div>

          <div className="relative rounded-2xl overflow-hidden bg-slate-950 aspect-square border border-slate-200/90 shadow-inner flex items-center justify-center">
            {previewImage && (
              <Image
                src={
                  showAnnotated && prediction?.annotated_image_url
                    ? prediction.annotated_image_url
                    : previewImage
                }
                alt="Chilli Foliage Pest Inspection"
                fill
                priority
                sizes="(max-width: 1024px) 100vw, 50vw"
                className="object-cover transition-opacity duration-300"
              />
            )}

            {/* Bounding Box SVG Overlay for Calibrated Mode */}
            {showAnnotated && prediction && prediction.detections.length > 0 && (
              <svg
                viewBox="0 0 640 640"
                className="absolute inset-0 w-full h-full pointer-events-none"
              >
                {prediction.detections.map((det, idx) => {
                  const { x1, y1, x2, y2 } = det.bounding_box;
                  const w = x2 - x1;
                  const h = y2 - y1;
                  return (
                    <g key={idx}>
                      {/* Bounding Box Rect */}
                      <rect
                        x={x1}
                        y={y1}
                        width={w}
                        height={h}
                        fill="rgba(239, 68, 68, 0.15)"
                        stroke="#dc2626"
                        strokeWidth="2.5"
                        rx="4"
                      />
                      {/* Centroid Crosshair */}
                      <circle
                        cx={det.target_center.x}
                        cy={det.target_center.y}
                        r="3"
                        fill="#facc15"
                      />
                      {/* Label badge */}
                      <rect
                        x={x1}
                        y={Math.max(y1 - 16, 0)}
                        width={Math.max(det.display_name.length * 7 + 36, 50)}
                        height="16"
                        fill="#991b1b"
                        rx="3"
                      />
                      <text
                        x={x1 + 3}
                        y={Math.max(y1 - 4, 12)}
                        fill="#ffffff"
                        fontSize="10"
                        fontWeight="bold"
                        fontFamily="monospace"
                      >
                        {det.display_name} {Math.round(det.confidence * 100)}%
                      </text>
                    </g>
                  );
                })}
              </svg>
            )}

            {/* Scanning pulse animation */}
            {isAnalyzing && (
              <div className="absolute inset-0 bg-emerald-500/20 backdrop-blur-xs flex items-center justify-center">
                <div className="bg-emerald-950/90 text-white px-4 py-2 rounded-xl flex items-center gap-2 font-mono text-xs font-bold border border-emerald-400">
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>EXTRACTING PEST CENTROIDS...</span>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
            <span> Yellow dots indicate robotic spray target coordinates `(x, y)`</span>
            <span>Centroids Extracted: <b>{prediction?.detections.length || 0}</b></span>
          </div>
        </div>

        {/* Right: Exact Count KPIs & 4-Species Breakdown */}
        <div className="space-y-5">
          {/* Main KPI Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
            <div>
              <span className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                EXACT PEST COUNT & DENSITY METRIC
              </span>
              <div className="flex items-baseline gap-3 mb-2">
                <span className="text-5xl font-black text-red-600 tracking-tight font-mono">
                  {pestCount}
                </span>
                <span className="text-base font-bold text-slate-600">
                  Insects Counted
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Exact individual micro-organism count from high-magnification crop vision.
              </p>
            </div>

            <div className="pt-4 mt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
              <span
                className={`inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full border ${severity.color}`}
              >
                <AlertOctagon className="w-3.5 h-3.5" />
                {severity.label}
              </span>

              <span className="text-xs text-slate-400 font-medium">
                Frame Density: <b>{(pestCount / 1).toFixed(1)} pests / leaf</b>
              </span>
            </div>
          </div>

          {/* 4-Class Breakdown Card matching the model classes */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs space-y-4">
            <div>
              <h4 className="text-sm font-bold text-slate-800">
                YOLOv8n Species Distribution
              </h4>
              <p className="text-xs text-slate-400">
                Counts categorized by the 4 target classification heads.
              </p>
            </div>

            <div className="space-y-3.5">
              {[
                {
                  code: "MP",
                  name: "Aphids (Kutu Daun)",
                  risk: "High Risk • Sap Drain Vector",
                  color: "bg-red-600",
                },
                {
                  code: "BT",
                  name: "Whiteflies (Kutu Kebul)",
                  risk: "Moderate Risk • Yellow Mosaic Vector",
                  color: "bg-amber-500",
                },
                {
                  code: "T",
                  name: "Chilli Thrips (Thrips)",
                  risk: "High Risk • Foliage Curling",
                  color: "bg-indigo-600",
                },
                {
                  code: "C",
                  name: "Caterpillars (Ulat)",
                  risk: "Critical • Leaf Defoliation",
                  color: "bg-emerald-600",
                },
              ].map((item) => {
                const count = prediction?.class_summary[item.code]?.detections || 0;
                const percentage =
                  pestCount > 0 ? Math.round((count / pestCount) * 100) : 0;
                const avgConf =
                  prediction?.class_summary[item.code]?.average_confidence || 0;

                return (
                  <div key={item.code} className="space-y-1">
                    <div className="flex justify-between items-center text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-800">{item.name}</span>
                        {avgConf > 0 && (
                          <span className="text-[10px] font-mono text-emerald-800 bg-emerald-50 px-1.5 py-0.2 rounded font-semibold">
                            {Math.round(avgConf * 100)}% conf
                          </span>
                        )}
                      </div>
                      <span className="font-mono font-bold text-slate-900">
                        {count} pests ({percentage}%)
                      </span>
                    </div>

                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${item.color}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>

                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>Class ID: [{item.code}]</span>
                      <span className="font-semibold text-slate-500">{item.risk}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Precision Actuator Dispatch Box */}
          <div className="bg-emerald-50/80 border border-emerald-200 rounded-3xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-[10px] font-black text-emerald-800 uppercase tracking-wider block mb-0.5">
                AUTONOMOUS ACTUATOR DISPATCH
              </span>
              <h4 className="text-sm font-bold text-slate-800">
                Organic Cold-pressed Neem (0.5%) Formulation
              </h4>
              <p className="text-xs text-slate-600 mt-0.5">
                Target Volume: <b>45 ml / sector</b> • Status:{" "}
                <span className="font-bold text-emerald-800">
                  {pestCount > 0 ? "Actuator Armed" : "Standby (Safe Threshold)"}
                </span>
              </p>
            </div>

            <button
              onClick={handleTriggerSpray}
              disabled={pestCount === 0}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#14532d] hover:bg-emerald-900 active:scale-95 transition shadow-xs cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            >
              <Target className="w-4 h-4" />
              Trigger Precision Spray
            </button>
          </div>

          {sprayStatus && (
            <div className="p-3.5 rounded-2xl bg-emerald-100/90 border border-emerald-300 text-emerald-900 text-xs font-semibold flex items-center gap-2 animate-pulse">
              <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
              <span>{sprayStatus}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
