"use client";

import React, { useState } from "react";
import ModelNavigationTabs from "@/components/analysis/ModelNavigationTabs";
import ChilliNpkRequirement from "@/components/analysis/ChilliNpkRequirement";
import SoilSensorComparison from "@/components/analysis/SoilSensorComparison";
import PaddyGapDetector from "@/components/analysis/PaddyGapDetector";
import PestCountQuantifier from "@/components/analysis/PestCountQuantifier";

/**
 * ANALYSIS PAGE (/analysis)
 * Features 4 distinct tabs to easily navigate and showcase all 4 team members' research models!
 */
export default function AnalysisPage() {
  const [activeModel, setActiveModel] = useState<
    "chilli" | "soil" | "paddy" | "pest"
  >("chilli");

  return (
    <div className="space-y-6">
      {/* 1. Page Header */}
      <div>
        <span className="block text-xs font-bold tracking-wider text-emerald-800 uppercase mb-1">
          RESEARCH PROJECT • 4-MODEL AGRIBOT ANALYTICS
        </span>
        <h1 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">
          Precision Agriculture AI & Telemetry Analysis
        </h1>
        <p className="text-xs text-slate-500 mt-1 max-w-3xl">
          Select any of the 4 research models below to review specific telemetry calculations, gap analyses, and exact pest quantifier diagnostics.
        </p>
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
