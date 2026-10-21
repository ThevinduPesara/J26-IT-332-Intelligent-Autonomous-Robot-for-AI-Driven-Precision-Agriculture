import React from "react";
import { Wifi } from "lucide-react";

interface NavigationHeaderProps {
  category: string;
  title: string;
  stepperOnlineBadge: string;
  rssi: string;
}

export default function NavigationHeader({
  category,
  title,
  stepperOnlineBadge,
  rssi,
}: NavigationHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      {/* Left: Category and Main Title */}
      <div>
        <span className="block text-xs font-bold tracking-wider text-emerald-800 uppercase mb-1">
          {category}
        </span>
        <h1 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">
          {title}
        </h1>
      </div>

      {/* Right: ESP32 Stepper Status & RSSI Badges */}
      <div className="flex flex-wrap items-center gap-2.5">
        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-100/90 text-emerald-800 border border-emerald-200">
          <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
          {stepperOnlineBadge}
        </span>

        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
          <Wifi className="w-3.5 h-3.5 text-slate-500" />
          RSSI: {rssi}
        </span>
      </div>
    </div>
  );
}
