"use client";

import React, { useState, useEffect } from "react";
import {
  Sprout,
  CheckCircle2,
  Calendar,
  AlertTriangle,
  Layers,
  Activity,
  Sparkles,
  Info,
  Camera,
  Play,
  Square,
  Zap,
  Sliders,
  Flame,
} from "lucide-react";
import { researchModelsData } from "@/data/researchModelsData";
import ModelMediaUploader from "@/components/analysis/ModelMediaUploader";
import {
  predictChilliImage,
  checkChilliApiHealth,
  getChilliAssetUrl,
  PredictionResponse,
} from "@/services/chilliApi";

export default function ChilliNpkRequirement() {
  const data = researchModelsData.chilliRequirement;

  // Backend state
  const [confidence, setConfidence] = useState<number>(0.25);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analyzedSuccess, setAnalyzedSuccess] = useState<boolean>(false);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] =
    useState<PredictionResponse | null>(null);
  const [activeImageView, setActiveImageView] = useState<
    "annotated" | "original"
  >("annotated");

  // Live Camera Stream state
  const [isLiveStreamActive, setIsLiveStreamActive] = useState<boolean>(false);
  const [liveStreamError, setLiveStreamError] = useState<string | null>(null);

  // Manual Fertilizer Dispenser Simulation Trigger
  const [dispenseStatus, setDispenseStatus] = useState<string | null>(null);

  const chilliSamples = [
    {
      label: "Chilli Leaf Sample #1 (N/K Def)",
      type: "image" as const,
      url: "/chilli_sample_1.jpg",
    },
    {
      label: "Chilli Leaf Sample #2 (Field Leaf)",
      type: "image" as const,
      url: "/chilli_sample_2.jpg",
    },
    {
      label: "Robotic Field Inspection (Video)",
      type: "video" as const,
      url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    },
  ];

  // Periodic health check of backend
  useEffect(() => {
    let isMounted = true;
    async function checkHealth() {
      const ok = await checkChilliApiHealth();
      if (isMounted) setApiOnline(ok);
    }
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Handle running inference
  const handleAnalyze = async (media: {
    file: File | null;
    url: string;
    type: "image" | "video";
    name: string;
  }) => {
    setErrorMsg(null);
    setIsAnalyzing(true);
    setAnalyzedSuccess(false);

    try {
      let fileToUpload = media.file;

      // If user selected sample URL without uploading local file, fetch as blob
      if (!fileToUpload) {
        const response = await fetch(media.url);
        const blob = await response.blob();
        fileToUpload = new File([blob], `${media.name.replace(/\s+/g, "_")}.jpg`, {
          type: blob.type || "image/jpeg",
        });
      }

      // Call FastAPI Backend
      const result = await predictChilliImage(fileToUpload, confidence);
      setPredictionResult(result);
      setAnalyzedSuccess(true);
      setActiveImageView("annotated");
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to connect to Chilli Detection API.";
      setErrorMsg(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Helper for UI styling of prediction class
  const getPredictionBadge = (pred: string) => {
    switch (pred) {
      case "Healthy":
        return {
          title: "Healthy Chilli Plant",
          badge: "No Nutrient Deficiency Detected",
          color: "text-emerald-700 bg-emerald-50 border-emerald-200",
          desc: "Optimal chlorophyll synthesis observed. Standard maintenance fertilization schedule recommended.",
          recommendedFertilizer: "Balanced NPK 20-20-20 (Maintenance 5g/plant)",
          dosage: "5.0 g / plant",
          urgency: "Normal / Maintenance",
        };
      case "N_Def":
        return {
          title: "Nitrogen (N) Deficiency Detected",
          badge: "Severe Chlorosis Alert",
          color: "text-amber-800 bg-amber-50 border-amber-200",
          desc: "Lower leaf pale yellowing detected. Foliar Urea or Nitrogen-rich liquid formulation recommended.",
          recommendedFertilizer: "Urea (46-0-0) / Liquid Nitrogen Mix",
          dosage: "12.5 g / plant",
          urgency: "High Priority (Apply within 48h)",
        };
      case "P_Def":
        return {
          title: "Phosphorus (P) Deficiency Detected",
          badge: "Purpling / Stunting Alert",
          color: "text-purple-800 bg-purple-50 border-purple-200",
          desc: "Anthocyanin purpling detected on leaf margins. Superphosphate / TSP application recommended.",
          recommendedFertilizer: "Triple Super Phosphate (TSP 0-46-0)",
          dosage: "8.0 g / plant",
          urgency: "Moderate Priority",
        };
      case "K_Def":
        return {
          title: "Potassium (K) Deficiency Detected",
          badge: "Marginal Leaf Necrosis Alert",
          color: "text-rose-800 bg-rose-50 border-rose-200",
          desc: "Leaf tip and marginal scorching detected. Muriate of Potash (MOP) supplement recommended.",
          recommendedFertilizer: "Muriate of Potash (MOP 0-0-60)",
          dosage: "15.0 g / plant",
          urgency: "Critical (Fruit Quality Risk)",
        };
      default:
        return {
          title: pred,
          badge: "AI Assessment Complete",
          color: "text-slate-800 bg-slate-50 border-slate-200",
          desc: "YOLO11s classification completed across detected vegetative regions.",
          recommendedFertilizer: "Custom NPK Formulation",
          dosage: "Calibrated dynamically",
          urgency: "Monitored",
        };
    }
  };

  const badgeInfo = predictionResult
    ? getPredictionBadge(predictionResult.overall_prediction)
    : null;

  const handleTriggerDispense = () => {
    setDispenseStatus("Sending command to Robotic NPK Dispenser Hoppers...");
    setTimeout(() => {
      setDispenseStatus("Command Dispatched! Dispensing valve open (Target: " + (badgeInfo?.dosage || "Standard Dose") + ")");
      setTimeout(() => setDispenseStatus(null), 5000);
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* 1. Overview Banner & API Status */}
      <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">
              MODEL 1 • CHILLI PHENOLOGY & NPK DEFICIENCY
            </span>
            {/* Backend connection pill */}
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${
                apiOnline
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : apiOnline === false
                  ? "bg-amber-50 text-amber-700 border-amber-200"
                  : "bg-slate-50 text-slate-500 border-slate-200"
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  apiOnline ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
                }`}
              />
              {apiOnline
                ? "FastAPI YOLO11s Online (Port 8000)"
                : apiOnline === false
                ? "Backend Offline (Port 8000)"
                : "Checking API..."}
            </span>
          </div>

          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Sprout className="w-3.5 h-3.5" />
            {data.badge}
          </span>
        </div>

        <h2 className="text-lg md:text-xl font-bold text-slate-800 mb-1">
          {data.title}
        </h2>
        <p className="text-xs text-slate-500 mb-4 max-w-3xl">
          {data.summary}
        </p>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div>
            Current Crop Stage:{" "}
            <span className="font-bold text-emerald-800">{data.cropStage}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Target Crop:{" "}
            <span className="font-semibold italic text-slate-700">
              {data.targetSpecies}
            </span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Classes: <span className="font-semibold text-slate-700">Healthy, N_Def, P_Def, K_Def</span>
          </div>
        </div>
      </div>

      {/* Backend error notice */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-800 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
          <div className="flex-1">
            <span className="font-bold block">Model Inference Error</span>
            <p className="mt-0.5 text-rose-700">{errorMsg}</p>
            <p className="mt-1 text-[11px] text-rose-500">
              Make sure FastAPI is running with: <code>uvicorn app.main:app --reload --port 8000</code> in the backend directory.
            </p>
          </div>
        </div>
      )}

      {/* 2. Photo & Video Upload / Live Inference Trigger */}
      <ModelMediaUploader
        modelName="Chilli NPK Prediction"
        description="Upload a chilli leaf photo or test sample to run YOLO11s inference and compute precise deficiency dosing."
        defaultSamples={chilliSamples}
        confidence={confidence}
        onConfidenceChange={setConfidence}
        isAnalyzing={isAnalyzing}
        analyzedSuccess={analyzedSuccess}
        onAnalyze={handleAnalyze}
      />

      {/* 3. Real-time Live Camera Stream Section (Direct FastAPI MJPEG) */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
              <Camera className="w-4 h-4 text-emerald-700" />
              Real-time Hardware Camera Stream (FastAPI YOLO MJPEG)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Stream live video directly from connected robot camera or server webcam with real-time YOLO bounding box overlays.
            </p>
          </div>

          <button
            onClick={() => {
              setLiveStreamError(null);
              setIsLiveStreamActive(!isLiveStreamActive);
            }}
            disabled={!apiOnline}
            className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer disabled:opacity-50 ${
              isLiveStreamActive
                ? "bg-rose-600 hover:bg-rose-700 text-white shadow-xs"
                : "bg-emerald-800 hover:bg-emerald-900 text-white shadow-xs"
            }`}
          >
            {isLiveStreamActive ? (
              <>
                <Square className="w-3.5 h-3.5 fill-current" /> Stop Live Stream
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" /> Start Live Stream
              </>
            )}
          </button>
        </div>

        {isLiveStreamActive && (
          <div className="relative rounded-xl overflow-hidden border border-slate-300 bg-slate-950 aspect-16/9 flex items-center justify-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={getChilliAssetUrl("/camera/stream")}
              alt="Live Chilli Detection MJPEG Stream"
              onError={() =>
                setLiveStreamError(
                  "Unable to load camera feed. Ensure server webcam/camera is plugged in and CAMERA_INDEX=0 is valid."
                )
              }
              className="w-full h-full object-contain"
            />
            {liveStreamError ? (
              <div className="absolute inset-0 bg-slate-900/90 flex flex-col items-center justify-center p-6 text-center text-rose-400">
                <AlertTriangle className="w-8 h-8 mb-2" />
                <span className="text-xs font-bold">{liveStreamError}</span>
                <span className="text-[11px] text-slate-400 mt-1">
                  Check if another application is using the camera or configure backend/.env
                </span>
              </div>
            ) : (
              <div className="absolute top-3 left-3 bg-rose-600/90 text-white px-2.5 py-1 rounded-md text-[10px] font-mono font-bold tracking-wider flex items-center gap-1.5 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-white animate-ping" />
                LIVE YOLO INFERENCE STREAM
              </div>
            )}
          </div>
        )}
      </div>

      {/* 4. Live AI Detection Output Section (Displayed upon inference) */}
      {predictionResult && badgeInfo && (
        <div className="bg-white rounded-2xl border border-emerald-200/90 shadow-sm p-6 space-y-6">
          {/* Header & Status Card */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold tracking-wide uppercase bg-emerald-100 text-emerald-800">
                  LIVE MODEL INFERENCE RESULTS
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  ID: #{predictionResult.request_id.slice(0, 8)}
                </span>
              </div>
              <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-700" />
                {badgeInfo.title}
              </h3>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="block text-[11px] font-bold text-slate-400 uppercase">
                  Confidence Score
                </span>
                <span className="text-lg font-extrabold text-emerald-800 font-mono">
                  {(predictionResult.overall_confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700">
                <Activity className="w-5 h-5" />
              </div>
            </div>
          </div>

          {/* Diagnostic message box */}
          <div className={`p-4 rounded-xl border ${badgeInfo.color} flex items-start gap-3`}>
            <Info className="w-5 h-5 shrink-0 mt-0.5" />
            <div className="flex-1 text-xs">
              <span className="font-bold block text-sm mb-0.5">
                {badgeInfo.badge}
              </span>
              <p className="leading-relaxed opacity-90">{badgeInfo.desc}</p>
            </div>
          </div>

          {/* Prescription & Automated Dispensing Recommendation Box */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                Agronomic Prescription & Dispenser Recommendation
              </span>
              <div className="text-xs font-bold text-slate-800">
                Fertilizer: <span className="text-emerald-800 font-semibold">{badgeInfo.recommendedFertilizer}</span>
              </div>
              <div className="text-[11px] text-slate-600 flex items-center gap-3">
                <span>Calculated Dose: <b className="text-slate-800">{badgeInfo.dosage}</b></span>
                <span>•</span>
                <span>Urgency: <b className="text-amber-800">{badgeInfo.urgency}</b></span>
              </div>
            </div>

            <div className="flex flex-col items-end gap-1.5">
              <button
                onClick={handleTriggerDispense}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-[#18533a] hover:bg-[#0f3c29] text-white shadow-xs transition active:scale-95 cursor-pointer"
              >
                <Zap className="w-3.5 h-3.5 fill-current" />
                Dispatch to Robotic Dispenser
              </button>
              {dispenseStatus && (
                <span className="text-[11px] font-semibold text-emerald-700 animate-pulse">
                  {dispenseStatus}
                </span>
              )}
            </div>
          </div>

          {/* Split View: Annotated YOLO Image on Left, Class Summary Table on Right */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
            {/* Left: Annotated Output Viewer */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-emerald-700" />
                  YOLO11s Output Feed
                </span>
                <div className="flex items-center rounded-lg bg-slate-100 p-0.5 text-xs font-semibold">
                  <button
                    onClick={() => setActiveImageView("annotated")}
                    className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                      activeImageView === "annotated"
                        ? "bg-white text-emerald-800 shadow-2xs"
                        : "text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    Annotated (Boxes)
                  </button>
                  <button
                    onClick={() => setActiveImageView("original")}
                    className={`px-2.5 py-1 rounded-md transition cursor-pointer ${
                      activeImageView === "original"
                        ? "bg-white text-emerald-800 shadow-2xs"
                        : "text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    Original
                  </button>
                </div>
              </div>

              <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-950 aspect-4/3 flex items-center justify-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={getChilliAssetUrl(
                    activeImageView === "annotated"
                      ? predictionResult.annotated_image_url
                      : predictionResult.original_image_url
                  )}
                  alt="Inference Result"
                  className="w-full h-full object-contain"
                />
                <div className="absolute bottom-2 left-2 bg-black/75 px-2.5 py-1 rounded-md text-[10px] text-white font-mono flex items-center gap-1.5">
                  <span>Detections: {predictionResult.number_of_detections}</span>
                  <span>•</span>
                  <span>Threshold: {Math.round(confidence * 100)}%</span>
                </div>
              </div>
            </div>

            {/* Right: Class breakdown cards and detailed metrics */}
            <div className="space-y-4">
              <span className="text-xs font-bold text-slate-700 block">
                Detection Breakdown by Deficiency Class
              </span>

              <div className="grid grid-cols-2 gap-3">
                {["Healthy", "N_Def", "P_Def", "K_Def"].map((clsName) => {
                  const summary = predictionResult.class_summary[clsName];
                  const hasDetections = (summary?.detections || 0) > 0;
                  const isOverall = predictionResult.overall_prediction === clsName;

                  return (
                    <div
                      key={clsName}
                      className={`p-3.5 rounded-xl border transition ${
                        isOverall
                          ? "bg-emerald-50/70 border-emerald-300 ring-1 ring-emerald-300"
                          : hasDetections
                          ? "bg-slate-50 border-slate-200"
                          : "bg-white border-slate-100 opacity-60"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-xs font-bold text-slate-800">
                          {clsName}
                        </span>
                        {isOverall && (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-emerald-700 text-white uppercase">
                            Primary
                          </span>
                        )}
                      </div>
                      <div className="space-y-1 text-[11px] text-slate-600 font-mono">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Instances:</span>
                          <span className="font-bold text-slate-800">
                            {summary?.detections || 0}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Peak Conf:</span>
                          <span className="font-bold text-slate-800">
                            {summary?.highest_confidence
                              ? `${(summary.highest_confidence * 100).toFixed(1)}%`
                              : "0%"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Avg Conf:</span>
                          <span className="font-bold text-slate-800">
                            {summary?.average_confidence
                              ? `${(summary.average_confidence * 100).toFixed(1)}%`
                              : "0%"}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Real-time Bounding Box List */}
              <div className="bg-slate-50 rounded-xl p-3 border border-slate-200 max-h-44 overflow-y-auto space-y-1.5 text-xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Identified Regions ({predictionResult.detections.length})
                </span>
                {predictionResult.detections.length === 0 ? (
                  <p className="text-[11px] text-slate-400 italic">
                    No individual instances exceeded the {Math.round(confidence * 100)}% threshold.
                  </p>
                ) : (
                  predictionResult.detections.map((det, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-white px-3 py-2 rounded-lg border border-slate-100 text-[11px]"
                    >
                      <span className="font-bold text-slate-700">
                        #{idx + 1} {det.class_name}
                      </span>
                      <span className="font-mono text-emerald-700 font-semibold">
                        {(det.confidence * 100).toFixed(1)}%
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        [{Math.round(det.bounding_box.x1)}, {Math.round(det.bounding_box.y1)}, {Math.round(det.bounding_box.x2)}, {Math.round(det.bounding_box.y2)}]
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. Target Requirements Cards (N, P, K) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {data.requirements.map((req) => {
          // Dynamic calculation based on detected deficiency
          const isDeficient =
            (req.element.startsWith("Nitrogen") && predictionResult?.overall_prediction === "N_Def") ||
            (req.element.startsWith("Phosphorus") && predictionResult?.overall_prediction === "P_Def") ||
            (req.element.startsWith("Potassium") && predictionResult?.overall_prediction === "K_Def");

          return (
            <div
              key={req.element}
              className={`bg-white rounded-2xl p-6 border shadow-xs flex flex-col justify-between transition ${
                isDeficient
                  ? "border-amber-400 ring-2 ring-amber-300/40 bg-amber-50/20"
                  : "border-slate-200/80"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    PREDICTED TARGET DEMAND
                  </span>
                  {isDeficient && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-100 text-amber-900 border border-amber-300">
                      DEFICIENCY TARGET
                    </span>
                  )}
                </div>

                <h3 className={`text-base font-bold ${req.color} mb-3`}>
                  {req.element}
                </h3>

                <div className="flex items-baseline gap-2 mb-3">
                  <span className="text-3xl md:text-4xl font-extrabold text-slate-800 tracking-tight">
                    {req.target}
                  </span>
                  <span className="text-xs font-semibold text-slate-400">
                    {req.unit}
                  </span>
                </div>

                <p className="text-xs text-slate-500 leading-relaxed mb-4">
                  {req.importance}
                </p>
              </div>

              <div
                className={`p-3 rounded-xl text-[11px] font-semibold flex items-center gap-1.5 ${
                  isDeficient
                    ? "bg-amber-100 text-amber-900"
                    : `${req.bg} ${req.color}`
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>
                  {isDeficient
                    ? "Dispenser auto-dosing active for this nutrient"
                    : "Optimal flowering formulation computed"}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 6. Growth Stages Timeline Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800">
              Chilli Phenological Stage NPK Demand Matrix
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Standard fertilizer demand profiles across development lifecycle.
            </p>
          </div>
          <Calendar className="w-4 h-4 text-slate-400" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/50 text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
                <th className="py-3.5 px-6">STAGE</th>
                <th className="py-3.5 px-6">NITROGEN (N)</th>
                <th className="py-3.5 px-6">PHOSPHORUS (P)</th>
                <th className="py-3.5 px-6">POTASSIUM (K)</th>
                <th className="py-3.5 px-6">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data.growthStages.map((stage) => (
                <tr
                  key={stage.stage}
                  className={`transition ${
                    stage.active
                      ? "bg-emerald-50/50 font-semibold"
                      : "hover:bg-slate-50/60"
                  }`}
                >
                  <td className="py-3.5 px-6 text-slate-800">{stage.stage}</td>
                  <td className="py-3.5 px-6 font-mono">{stage.n}</td>
                  <td className="py-3.5 px-6 font-mono">{stage.p}</td>
                  <td className="py-3.5 px-6 font-mono">{stage.k}</td>
                  <td className="py-3.5 px-6">
                    {stage.active ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[11px] font-bold">
                        Current Active Phase
                      </span>
                    ) : (
                      <span className="text-slate-400 text-[11px]">
                        Completed / Upcoming
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
