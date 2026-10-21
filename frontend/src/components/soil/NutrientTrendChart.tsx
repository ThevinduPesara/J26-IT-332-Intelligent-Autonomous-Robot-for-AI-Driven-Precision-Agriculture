import React from "react";

interface LegendItem {
  name: string;
  color: string;
}

interface NutrientTrendChartProps {
  title: string;
  subtitle: string;
  legend: LegendItem[];
  timeLabels: string[];
}

export default function NutrientTrendChart({
  title,
  subtitle,
  legend,
  timeLabels,
}: NutrientTrendChartProps) {
  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      {/* Top Header: Title, Subtitle and NPK Color Legend */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <h2 className="text-base font-bold text-slate-800">{title}</h2>
          <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
        </div>

        {/* Legend dots */}
        <div className="flex items-center gap-3">
          {legend.map((item) => (
            <div key={item.name} className="flex items-center gap-1.5 text-xs font-semibold text-slate-600">
              <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
              <span>{item.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* SVG Trend Graph Area */}
      <div className="relative w-full h-52 my-2">
        {/* Background Grid Lines */}
        <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-40">
          <div className="border-b border-slate-200 w-full" />
          <div className="border-b border-slate-200 w-full" />
          <div className="border-b border-slate-200 w-full" />
          <div className="border-b border-slate-200 w-full" />
        </div>

        {/* Smooth Curved SVG Wave Lines */}
        <svg
          viewBox="0 0 500 200"
          preserveAspectRatio="none"
          className="w-full h-full relative z-10"
        >
          {/* Curve 1: Potassium (K) - Teal Top Curve */}
          <path
            d="M 0 100 C 70 95, 140 105, 210 110 C 280 115, 330 65, 410 65 C 450 65, 480 85, 500 100"
            fill="none"
            stroke="#0f766e"
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Curve 2: Nitrogen (N) - Dark Green Mid Curve */}
          <path
            d="M 0 135 C 70 130, 150 140, 220 135 C 300 130, 360 85, 430 90 C 470 95, 485 110, 500 128"
            fill="none"
            stroke="#14532d"
            strokeWidth="3"
            strokeLinecap="round"
          />

          {/* Curve 3: Phosphorus (P) - Brown Lower Curve */}
          <path
            d="M 0 160 C 60 155, 120 158, 200 160 C 270 162, 340 145, 400 140 C 440 138, 470 145, 500 155"
            fill="none"
            stroke="#92400e"
            strokeWidth="3"
            strokeLinecap="round"
          />
        </svg>
      </div>

      {/* X-Axis Timeline Labels */}
      <div className="flex justify-between items-center text-[11px] font-mono text-slate-400 pt-4 border-t border-slate-100">
        {timeLabels.map((label) => (
          <span key={label}>{label}</span>
        ))}
      </div>
    </div>
  );
}
