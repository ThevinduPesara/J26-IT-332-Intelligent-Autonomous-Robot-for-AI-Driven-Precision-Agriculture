"use client";

import React, { useState } from "react";
import { FlaskConical, RefreshCw } from "lucide-react";

interface NpkHeaderProps {
  title: string;
  sensorBadge: string;
  description: string;
}

export default function NpkHeader({
  title,
  sensorBadge,
  description,
}: NpkHeaderProps) {
  const [isReading, setIsReading] = useState(false);

  const handleReadSensors = () => {
    setIsReading(true);
    setTimeout(() => {
      setIsReading(false);
      alert("Probed sensor telemetry synchronized successfully!");
    }, 1200);
  };

  return (
    <div className="bg-white rounded-2xl p-5 md:p-6 border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      {/* Left: Flask Icon, Title, and Subtitle */}
      <div className="flex items-center gap-3.5">
        <div className="w-12 h-12 rounded-2xl bg-[#0f5132] text-white flex items-center justify-center shrink-0 shadow-sm">
          <FlaskConical className="w-6 h-6" />
        </div>
        <div>
          <div className="flex flex-wrap items-center gap-2.5 mb-1">
            <h1 className="text-base md:text-lg font-bold text-slate-800">
              {title}
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100/90 text-emerald-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
              {sensorBadge}
            </span>
          </div>
          <p className="text-xs text-slate-500 max-w-xl">
            {description}
          </p>
        </div>
      </div>

      {/* Right: Read NPK Sensors Button */}
      <button
        onClick={handleReadSensors}
        disabled={isReading}
        className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-[#0f5132] hover:bg-emerald-900 active:scale-98 transition shadow-xs cursor-pointer shrink-0 disabled:opacity-75"
      >
        <RefreshCw className={`w-4 h-4 ${isReading ? "animate-spin" : ""}`} />
        {isReading ? "Reading..." : "Read NPK Sensors"}
      </button>
    </div>
  );
}
