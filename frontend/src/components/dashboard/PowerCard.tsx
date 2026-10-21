import React from "react";
import { Zap } from "lucide-react";

interface PowerCardProps {
  percentage: number;
  solarChargeRate: string;
  voltage: string;
  estimatedRuntime: string;
}

export default function PowerCard({
  percentage,
  solarChargeRate,
  voltage,
  estimatedRuntime,
}: PowerCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        {/* Header with Title & Icon */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">
            POWER & ENERGY
          </span>
          <Zap className="w-5 h-5 text-emerald-600" />
        </div>

        {/* Big Percentage & Solar Text */}
        <div className="flex items-baseline gap-3 mb-3">
          <span className="text-4xl md:text-5xl font-extrabold text-slate-800 tracking-tight">
            {percentage}%
          </span>
          <span className="text-xs font-semibold text-emerald-600">
            {solarChargeRate}
          </span>
        </div>

        {/* Battery Progress Bar */}
        <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden mb-6">
          <div
            className="bg-emerald-600 h-full rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Footer Details: Voltage & Estimated Runtime */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100">
        <div>
          <span className="block text-xs font-medium text-slate-400 mb-0.5">
            Voltage
          </span>
          <span className="text-sm font-bold text-slate-800">{voltage}</span>
        </div>
        <div>
          <span className="block text-xs font-medium text-slate-400 mb-0.5">
            Estimated Runtime
          </span>
          <span className="text-sm font-bold text-slate-800">
            {estimatedRuntime}
          </span>
        </div>
      </div>
    </div>
  );
}
