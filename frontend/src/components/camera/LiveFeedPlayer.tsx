"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Camera,
  Layers,
  Maximize2,
  Wifi,
  Video,
  VideoOff,
  AlertCircle,
} from "lucide-react";

interface LiveFeedPlayerProps {
  cameraInfo: {
    name: string;
    resolutionFps: string;
    irStatus: string;
    connectionStatus: string;
    recDuration: string;
    battery: string;
    signal: string;
    date: string;
    zoom: string;
    focus: string;
    grid: string;
  };
  detectedBBoxes: Array<{
    id: string;
    confidence: string;
    label: string;
    x: string;
    y: string;
    width: string;
    height: string;
  }>;
}

export default function LiveFeedPlayer({
  cameraInfo,
  detectedBBoxes,
}: LiveFeedPlayerProps) {
  // Default showAiOverlay to false so green bounding boxes are hidden
  const [showAiOverlay, setShowAiOverlay] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Turn ON Web Camera
  const startCamera = async () => {
    setCameraError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera API not supported on this device/browser.");
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "environment",
        },
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraActive(true);
    } catch (err: any) {
      console.error("Camera access error:", err);
      setCameraError(
        err.name === "NotAllowedError" || err.name === "PermissionDeniedError"
          ? "Camera permission denied. Please allow camera access in your browser settings."
          : "Unable to access camera hardware. Showing field simulation feed."
      );
      setIsCameraActive(false);
    }
  };

  // Turn OFF Web Camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  const toggleCamera = () => {
    if (isCameraActive) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  // Clean up stream when component unmounts
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Capture Image Frame snapshot
  const handleCaptureImage = () => {
    if (isCameraActive && videoRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = videoRef.current.videoWidth || 1280;
      canvas.height = videoRef.current.videoHeight || 720;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.download = `agribot_camera_snap_${Date.now()}.png`;
        link.href = dataUrl;
        link.click();
      }
    } else {
      alert("Captured frame from Field Simulation Stream saved to logs!");
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {/* Top Meta Header: Camera Name & Badges */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              isCameraActive ? "bg-emerald-500 animate-pulse" : "bg-emerald-600"
            }`}
          />
          <h2 className="text-base md:text-lg font-bold text-slate-800">
            {cameraInfo.name}
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
          <span className="px-2.5 py-1 rounded-md bg-slate-200 text-slate-700">
            {isCameraActive ? "Live WebCam Stream" : cameraInfo.resolutionFps}
          </span>
          <span className="px-2.5 py-1 rounded-md bg-slate-200 text-slate-700">
            {cameraInfo.irStatus}
          </span>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800">
            <Wifi className="w-3.5 h-3.5" />
            {cameraInfo.connectionStatus}
          </span>
        </div>
      </div>

      {/* Main Video Screen Container */}
      <div className="relative w-full aspect-16/10 md:aspect-16/9 bg-slate-900 rounded-2xl overflow-hidden shadow-md border border-slate-200 group">
        {/* 1. Real Webcam Video Element (shown when camera is ON) */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-500 ${
            isCameraActive ? "opacity-100 z-0" : "opacity-0 pointer-events-none"
          }`}
        />

        {/* 2. Farm Field Simulation Background (shown when camera is OFF) */}
        {!isCameraActive && (
          <div
            className="absolute inset-0 bg-cover bg-center transition-transform duration-700"
            style={{
              backgroundImage: `radial-gradient(ellipse at center, rgba(30,41,59,0.2) 0%, rgba(15,23,42,0.7) 100%), url('https://images.unsplash.com/photo-1592417817098-8f3d6eb228cc?auto=format&fit=crop&w=1600&q=80')`,
            }}
          />
        )}

        {/* Video HUD Overlays */}
        <div className="absolute inset-0 p-4 md:p-6 flex flex-col justify-between pointer-events-none select-none z-10">
          {/* Top HUD Info: REC badge only (Battery & Signal removed) */}
          <div className="flex justify-between items-start text-xs font-mono text-white/90">
            {/* Left: REC badge and location info */}
            <div className="space-y-1">
              <div className="inline-flex items-center gap-2 bg-black/60 backdrop-blur-md px-2.5 py-1 rounded-lg border border-white/10">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                <span className="font-bold text-red-400">REC</span>
                <span>{cameraInfo.recDuration}</span>
              </div>
              <div className="text-[11px] text-white/70 bg-black/40 px-2 py-1 rounded backdrop-blur-xs w-fit">
                CHILLI PLOT 1A • STATUS: ACTIVE
              </div>
            </div>
          </div>

          {/* Camera Error Message Notification if permission denied */}
          {cameraError && (
            <div className="bg-red-950/80 border border-red-500/50 text-red-200 text-xs px-3 py-2 rounded-xl backdrop-blur-md flex items-center gap-2 pointer-events-auto max-w-md mx-auto">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{cameraError}</span>
            </div>
          )}

          {/* AI Bounding Boxes (Only visible if explicitly toggled on) */}
          {showAiOverlay && (
            <div className="absolute inset-0 pointer-events-none">
              {/* Box 1: Capsicum annuum */}
              <div
                className="absolute border-2 border-emerald-400 rounded-lg bg-emerald-500/10 transition-all duration-300"
                style={{
                  top: detectedBBoxes[0].y,
                  left: detectedBBoxes[0].x,
                  width: detectedBBoxes[0].width,
                  height: detectedBBoxes[0].height,
                }}
              >
                <div className="absolute -top-7 left-0 bg-emerald-700 text-white text-[10px] font-mono font-semibold px-2 py-0.5 rounded shadow-sm">
                  ID: {detectedBBoxes[0].id} ({detectedBBoxes[0].confidence})
                </div>
                <div className="absolute bottom-1 left-1 text-[10px] font-semibold text-emerald-200 bg-black/60 px-1.5 py-0.5 rounded">
                  {detectedBBoxes[0].label}
                </div>
              </div>

              {/* Box 2: Seedling */}
              <div
                className="absolute border-2 border-teal-400 rounded-lg bg-teal-500/10 transition-all duration-300"
                style={{
                  top: detectedBBoxes[1].y,
                  left: detectedBBoxes[1].x,
                  width: detectedBBoxes[1].width,
                  height: detectedBBoxes[1].height,
                }}
              >
                <div className="absolute top-2 left-2 bg-emerald-100/90 text-emerald-900 text-[10px] font-mono font-bold px-2 py-0.5 rounded shadow-sm border border-emerald-300">
                  ID: {detectedBBoxes[1].id} ({detectedBBoxes[1].confidence})
                </div>
                <div className="absolute bottom-1 right-1 text-[10px] font-semibold text-white bg-black/60 px-1.5 py-0.5 rounded">
                  {detectedBBoxes[1].label}
                </div>
              </div>
            </div>
          )}

          {/* Bottom HUD: Video Controls and Telemetry Footer */}
          <div className="flex flex-wrap items-center justify-between gap-3 pointer-events-auto">
            {/* Control Action Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Camera ON / OFF Toggle Button */}
              <button
                onClick={toggleCamera}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold backdrop-blur-md transition active:scale-95 cursor-pointer shadow-sm ${
                  isCameraActive
                    ? "bg-red-600/90 hover:bg-red-700 text-white border border-red-500/50 shadow-red-600/20"
                    : "bg-emerald-600/90 hover:bg-emerald-700 text-white border border-emerald-500/50 shadow-emerald-600/20"
                }`}
              >
                {isCameraActive ? (
                  <>
                    <VideoOff className="w-3.5 h-3.5" />
                    Turn OFF Camera
                  </>
                ) : (
                  <>
                    <Video className="w-3.5 h-3.5" />
                    Turn ON Camera
                  </>
                )}
              </button>

              {/* Capture Snapshot Button */}
              <button
                onClick={handleCaptureImage}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-black/60 hover:bg-black/80 text-white backdrop-blur-md border border-white/20 transition active:scale-95 cursor-pointer"
              >
                <Camera className="w-3.5 h-3.5" />
                Capture Image
              </button>

              {/* Toggle AI Overlay Button */}
              <button
                onClick={() => setShowAiOverlay(!showAiOverlay)}
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold backdrop-blur-md border transition active:scale-95 cursor-pointer ${
                  showAiOverlay
                    ? "bg-emerald-600/80 hover:bg-emerald-600 text-white border-emerald-400/50"
                    : "bg-black/60 hover:bg-black/80 text-white/80 border-white/20"
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                Toggle AI Overlay
              </button>
            </div>

            {/* Camera settings details and fullscreen */}
            <div className="flex items-center gap-4 text-xs font-mono text-white/80 bg-black/50 px-3 py-1.5 rounded-xl backdrop-blur-md border border-white/10">
              <span>ZOOM: {cameraInfo.zoom}</span>
              <span>FOCUS: {cameraInfo.focus}</span>
              <span>GRID: {cameraInfo.grid}</span>
              <button
                onClick={() => alert("Full screen triggered.")}
                className="hover:text-white transition cursor-pointer"
                title="Fullscreen"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
