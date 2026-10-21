"use client";

import React, { useEffect, useState } from "react";
import Image from "next/image";
import { AlertTriangle, Grid, Layers, Sprout } from "lucide-react";
import { researchModelsData } from "@/data/researchModelsData";
import ModelMediaUploader from "@/components/analysis/ModelMediaUploader";
import {
  checkPaddyApiHealth,
  getPaddyModels,
  PaddyModel,
  PaddyPredictionResponse,
  predictPaddyImage,
} from "@/services/paddyApi";

export default function PaddyGapDetector() {
  const data = researchModelsData.paddyGap;
  const [models, setModels] = useState<PaddyModel[]>([]);
  const [selectedModel, setSelectedModel] = useState("segformer_base");
  const [alpha, setAlpha] = useState(0.52);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState<PaddyPredictionResponse | null>(null);

  const paddySamples = [
    {
      label: "Drone Aerial View (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Row Discontinuity Grid (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=1000&q=80",
    },
  ];

  useEffect(() => {
    let isCurrent = true;

    const refreshApiStatus = async () => {
      try {
        const [isOnline, response] = await Promise.all([
          checkPaddyApiHealth(),
          getPaddyModels(),
        ]);
        if (!isCurrent) return;
        setBackendOnline(isOnline);
        setModels(response.models);
        const availableModel = response.models.find((model) => model.available);
        if (availableModel) setSelectedModel(availableModel.id);
      } catch {
        if (isCurrent) setBackendOnline(false);
      }
    };

    void refreshApiStatus();
    const statusInterval = setInterval(() => void refreshApiStatus(), 10000);

    return () => {
      isCurrent = false;
      clearInterval(statusInterval);
    };
  }, []);

  const handleAnalyze = async (media: {
    file: File | null;
    url: string;
    type: "image" | "video";
  }) => {
    setErrorMessage("");
    setResult(null);

    if (media.type !== "image") {
      setErrorMessage("PaddyVision accepts still images; video analysis is not available.");
      return;
    }
    if (backendOnline !== true) {
      setErrorMessage("PaddyVision API is offline. Start the backend on port 8001 and retry.");
      return;
    }
    if (!models.some((model) => model.id === selectedModel && model.available)) {
      setErrorMessage("No trained checkpoint is available for the selected model.");
      return;
    }

    setIsAnalyzing(true);
    try {
      let file = media.file;
      if (!file) {
        const sampleResponse = await fetch(media.url);
        if (!sampleResponse.ok) {
          throw new Error("Could not load this sample image. Upload an image from your device instead.");
        }
        const imageBlob = await sampleResponse.blob();
        file = new File([imageBlob], "paddy-sample-image.jpg", {
          type: imageBlob.type || "image/jpeg",
        });
      }
      if (file.size > 15 * 1024 * 1024) {
        throw new Error("Image exceeds the 15 MB upload limit.");
      }
      setResult(await predictPaddyImage(file, selectedModel, alpha));
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "PaddyVision inference failed.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">
            MODEL 3 • PADDY CROP CONTINUITY & GAP DETECTION
          </span>
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
              backendOnline === true
                ? "bg-emerald-100 text-emerald-800 border-emerald-200"
                : backendOnline === false
                  ? "bg-amber-50 text-amber-800 border-amber-200"
                  : "bg-slate-100 text-slate-600 border-slate-200"
            }`}
          >
            <Grid className="w-3.5 h-3.5" />
            {backendOnline === true
              ? "PaddyVision API online"
              : backendOnline === false
                ? "PaddyVision API offline"
                : "Connecting to PaddyVision"}
          </span>
        </div>

        <h2 className="text-lg md:text-xl font-bold text-slate-800 mb-1">
          {data.title}
        </h2>
        <p className="text-xs text-slate-500 mb-4 max-w-3xl">{data.summary}</p>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div>
            Crop: <span className="font-bold text-slate-800">{data.cropType}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Model: <span className="font-semibold text-slate-700">{data.badge}</span>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose-600" />
          <div>
            <span className="block font-bold">PaddyVision inference error</span>
            <p className="mt-0.5">{errorMessage}</p>
            {backendOnline === false && (
              <p className="mt-1 text-rose-600">
                Start the API from the PaddyVision Studio folder with{" "}
                <code>uvicorn backend.main:app --reload --port 8001</code>.
              </p>
            )}
          </div>
        </div>
      )}

      <ModelMediaUploader
        modelName="Paddy Gap Detection"
        description="Upload a paddy-field image to segment existing plants, soil, and weeds with a trained PaddyVision model."
        defaultSamples={paddySamples}
        isAnalyzing={isAnalyzing}
        analyzedSuccess={result !== null}
        accept="image/*"
        uploadPrompt="Upload a paddy field image"
        uploadHint="JPEG or PNG · maximum 15 MB"
        onAnalyze={handleAnalyze}
      />

      <div className="flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-4">
        <label className="flex min-w-56 flex-1 flex-col gap-1.5 text-xs font-semibold text-slate-700">
          Segmentation model
          <select
            value={selectedModel}
            onChange={(event) => setSelectedModel(event.target.value)}
            disabled={!models.some((model) => model.available) || isAnalyzing}
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm disabled:bg-slate-100"
          >
            {models.length === 0 && <option value="segformer_base">Loading models...</option>}
            {models.map((model) => (
              <option key={model.id} value={model.id} disabled={!model.available}>
                {model.name}{model.available ? "" : " (checkpoint unavailable)"}
              </option>
            ))}
          </select>
        </label>
        <label className="flex min-w-56 flex-1 flex-col gap-1.5 text-xs font-semibold text-slate-700">
          Overlay opacity <span className="font-mono text-emerald-800">{Math.round(alpha * 100)}%</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={alpha}
            onChange={(event) => setAlpha(Number(event.target.value))}
            disabled={isAnalyzing}
            className="h-10 accent-emerald-700"
          />
        </label>
      </div>

      {backendOnline === true && models.length > 0 && !models.some((model) => model.available) && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-900">
          PaddyVision is running, but no model checkpoints were found. Check the configured project root and trained model files.
        </div>
      )}

      {result && (
        <section className="space-y-4" aria-live="polite">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Segmentation result</h3>
              <p className="mt-1 text-xs text-slate-500">
                {result.model_name} · {result.width} × {result.height} px · {result.inference_seconds.toFixed(2)} s · {result.device}
              </p>
            </div>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-1.5 text-xs font-semibold text-emerald-800">
              <Sprout className="h-3.5 w-3.5" />
              Mean confidence {Math.round(result.mean_confidence * 100)}%
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <figure className="overflow-hidden rounded-lg border border-slate-200 bg-slate-950">
              <Image
                src={`data:image/png;base64,${result.images.overlay_png}`}
                alt="Paddy field image with model segmentation overlay"
                width={result.width}
                height={result.height}
                unoptimized
                className="h-auto max-h-[480px] w-full object-contain"
              />
              <figcaption className="border-t border-slate-700 px-3 py-2 text-xs font-medium text-white">Segmentation overlay</figcaption>
            </figure>
            <figure className="overflow-hidden rounded-lg border border-slate-200 bg-slate-950">
              <Image
                src={`data:image/png;base64,${result.images.mask_png}`}
                alt="Color-coded PaddyVision segmentation mask"
                width={result.width}
                height={result.height}
                unoptimized
                className="h-auto max-h-[480px] w-full object-contain"
              />
              <figcaption className="border-t border-slate-700 px-3 py-2 text-xs font-medium text-white">Class mask</figcaption>
            </figure>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {result.stats.map((stat) => (
              <div key={stat.id} className="rounded-lg border border-slate-200 bg-white p-4">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                  <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: stat.color }} />
                  {stat.name}
                </div>
                <p className="mt-2 text-2xl font-extrabold text-slate-800">{stat.percent.toFixed(2)}%</p>
                <p className="mt-1 text-xs text-slate-500">
                  {stat.pixels.toLocaleString()} pixels
                  {stat.mean_confidence === null
                    ? ""
                    : ` · ${Math.round(stat.mean_confidence * 100)}% class confidence`}
                </p>
              </div>
            ))}
          </div>

          
        </section>
      )}
    </div>
  );
}
