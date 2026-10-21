"use client";

import React, { useState } from "react";
import ModelNavigationTabs from "@/components/analysis/ModelNavigationTabs";
import ChilliNpkRequirement from "@/components/analysis/ChilliNpkRequirement";
import SoilSensorComparison from "@/components/analysis/SoilSensorComparison";
import PaddyGapDetector from "@/components/analysis/PaddyGapDetector";
import PestCountQuantifier from "@/components/analysis/PestCountQuantifier";
import { Sparkles, ShieldCheck } from "lucide-react";

/**
 * HIGH-IMPACT PREMIUM ANALYSIS PAGE (/analysis)
 * Features dynamic telemetry indicators, interactive research model tabs, and high-visibility metrics.
 */
export default function AnalysisPage() {
  const [activeModel, setActiveModel] = useState<
    "chilli" | "soil" | "paddy" | "pest"
  >("chilli");

  return (
    <div className="space-y-6">
      {/* 1. Hero Analytics Banner with Glassmorphism & High-contrast Badges */}
      <div className="relative overflow-hidden rounded-3xl bg-linear-to-r from-emerald-950 via-slate-900 to-teal-950 text-white p-7 md:p-8 shadow-xl border border-emerald-800/40">
        {/* Ambient glow backgrounds */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2.5">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-extrabold uppercase tracking-widest bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 backdrop-blur-md">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                AgriBot Edge Intelligence Suite
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-white/10 text-slate-200 border border-white/10 backdrop-blur-md">
                <ShieldCheck className="w-3.5 h-3.5 text-teal-300" />
                YOLO11s + In-situ Calibrated
              </span>
            </div>

            <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white drop-shadow-xs">
              Precision Crop Telemetry & AI Model Suite
            </h1>
            <p className="text-xs md:text-sm text-slate-300/90 leading-relaxed font-normal">
              Continuous field diagnosis comparing deep learning vision inference with real-time subsurface NPK sensing and autonomous actuator dispatch.
            </p>
          </div>
        </div>
      </div>

      {/* 2. Top Navigation Tabs: 4 Research Models */}
      <section>
        <ModelNavigationTabs
          activeModel={activeModel}
          onSelectModel={setActiveModel}
        />
      </section>

      {/* 3. Dynamic Model View */}
      <section className="transition-all duration-300">
        {activeModel === "chilli" && <ChilliNpkRequirement />}
        {activeModel === "soil" && <SoilSensorComparison />}
        {activeModel === "paddy" && <PaddyGapDetector />}
        {activeModel === "pest" && <PestCountQuantifier />}
      </section>
    </div>
  );
}
