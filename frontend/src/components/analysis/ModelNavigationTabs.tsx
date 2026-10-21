import React from "react";
import { Sprout, Scale, Grid, Bug, ChevronRight } from "lucide-react";

interface ModelNavigationTabsProps {
  activeModel: "chilli" | "soil" | "paddy" | "pest";
  onSelectModel: (model: "chilli" | "soil" | "paddy" | "pest") => void;
}

export default function ModelNavigationTabs({
  activeModel,
  onSelectModel,
}: ModelNavigationTabsProps) {
  const models = [
    {
      id: "chilli" as const,
      num: "01",
      name: "Chilli NPK Requirement",
      sub: "YOLO11s Vision Deficiency",
      tag: "Live API",
      tagColor: "bg-emerald-500/20 text-emerald-300 border-emerald-400/30",
      icon: Sprout,
    },
    {
      id: "soil" as const,
      num: "02",
      name: "Soil Sensor vs. Deficiency",
      sub: "Electrochemical Calibration",
      tag: "Sensors",
      tagColor: "bg-teal-500/20 text-teal-300 border-teal-400/30",
      icon: Scale,
    },
    {
      id: "paddy" as const,
      num: "03",
      name: "Paddy Crop Gap Detection",
      sub: "Canopy Continuity Mapper",
      tag: "Spatial",
      tagColor: "bg-amber-500/20 text-amber-300 border-amber-400/30",
      icon: Grid,
    },
    {
      id: "pest" as const,
      num: "04",
      name: "Precise Pest Counting",
      sub: "Micro-Insect Density Metric",
      tag: "Quantifier",
      tagColor: "bg-rose-500/20 text-rose-300 border-rose-400/30",
      icon: Bug,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {models.map((m) => {
        const Icon = m.icon;
        const isActive = activeModel === m.id;

        return (
          <button
            key={m.id}
            onClick={() => onSelectModel(m.id)}
            className={`group relative overflow-hidden rounded-2xl p-4.5 text-left border transition-all duration-300 cursor-pointer flex flex-col justify-between ${
              isActive
                ? "bg-linear-to-br from-[#12422e] to-[#0a2e20] border-emerald-500 text-white shadow-lg shadow-emerald-950/20 ring-2 ring-emerald-400/50 scale-[1.02]"
                : "bg-white border-slate-200/90 text-slate-700 hover:border-emerald-300 hover:shadow-md hover:scale-[1.01]"
            }`}
          >
            {/* Top row: Icon and model number badge */}
            <div className="flex items-center justify-between mb-3 w-full">
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110 ${
                  isActive
                    ? "bg-white/20 text-white shadow-inner"
                    : "bg-emerald-50 text-emerald-800"
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                    isActive
                      ? m.tagColor
                      : "bg-slate-100 text-slate-600 border-slate-200"
                  }`}
                >
                  {m.tag}
                </span>
                <span
                  className={`text-xs font-mono font-black ${
                    isActive ? "text-emerald-300" : "text-slate-300"
                  }`}
                >
                  {m.num}
                </span>
              </div>
            </div>

            {/* Bottom text */}
            <div>
              <span
                className={`block text-xs font-bold leading-tight tracking-tight ${
                  isActive ? "text-white" : "text-slate-800"
                }`}
              >
                {m.name}
              </span>
              <span
                className={`block text-[11px] mt-1 font-medium ${
                  isActive ? "text-emerald-100/80" : "text-slate-400"
                }`}
              >
                {m.sub}
              </span>
            </div>

            {/* Active bottom accent bar */}
            {isActive && (
              <div className="absolute bottom-0 inset-x-0 h-1 bg-linear-to-r from-emerald-400 to-teal-300" />
            )}
          </button>
        );
      })}
    </div>
  );
}
