"use client";

import React from "react";
import { OctagonX, Home, FlaskConical } from "lucide-react";

interface HeroBannerProps {
  unitName: string;
  statusBadge: string;
  description: string;
  onEmergencyStop?: () => void;
  onReturnHome?: () => void;
  onQuickNPK?: () => void;
}

export default function HeroBanner({
  unitName,
  statusBadge,
  description,
  onEmergencyStop = () => alert("Emergency Stop Triggered!"),
  onReturnHome = () => alert("Return to Home initiated."),
  onQuickNPK = () => alert("Reading NPK Sensors..."),
}: HeroBannerProps) {
  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        {/* Subheader and Status Badge */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            AGRIBOT TELEMETRY GATEWAY
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#dcfce7] text-emerald-800">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
            {statusBadge}
          </span>
        </div>

        {/* Title */}
        <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight mb-2">
          {unitName}
        </h2>

        {/* Description */}
        <p className="text-sm text-slate-600 leading-relaxed max-w-2xl mb-6">
          {description}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Emergency Stop Button */}
        <button
          onClick={onEmergencyStop}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-[#b91c1c] hover:bg-red-800 active:scale-[0.98] transition shadow-xs cursor-pointer"
        >
          <OctagonX className="w-4 h-4" />
          Emergency Stop
        </button>

        {/* Return to Home Button */}
        <button
          onClick={onReturnHome}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-[#14532d] hover:bg-emerald-900 active:scale-[0.98] transition shadow-xs cursor-pointer"
        >
          <Home className="w-4 h-4" />
          Return to Home
        </button>

        {/* Quick NPK Read Button */}
        <button
          onClick={onQuickNPK}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200/80 active:scale-[0.98] transition cursor-pointer"
        >
          <FlaskConical className="w-4 h-4 text-slate-500" />
          Quick NPK Read
        </button>
      </div>
    </div>
  );
}
