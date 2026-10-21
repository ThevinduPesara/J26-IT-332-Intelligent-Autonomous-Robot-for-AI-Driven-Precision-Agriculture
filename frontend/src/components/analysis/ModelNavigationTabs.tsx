import React from "react";
import { Sprout, Scale, Grid, Bug } from "lucide-react";

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
      name: "Chilli NPK Requirement",
      sub: "Model 1: Crop Phenology Demand",
      icon: Sprout,
    },
    {
      id: "soil" as const,
      name: "Soil Sensor vs. Deficiency",
      sub: "Model 2: Live Sensor Comparator",
      icon: Scale,
    },
    {
      id: "paddy" as const,
      name: "Paddy Crop Gap Detection",
      sub: "Model 3: Rice Field Discontinuity",
      icon: Grid,
    },
    {
      id: "pest" as const,
      name: "Precise Pest Counting",
      sub: "Model 4: Exact Insect Quantifier",
      icon: Bug,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
      {models.map((m) => {
        const Icon = m.icon;
        const isActive = activeModel === m.id;

        return (
          <button
            key={m.id}
            onClick={() => onSelectModel(m.id)}
            className={`flex items-center gap-3.5 p-4 rounded-2xl text-left border transition-all duration-200 cursor-pointer ${
              isActive
                ? "bg-[#14532d] border-[#14532d] text-white shadow-md shadow-emerald-950/15"
                : "bg-white border-slate-200/90 text-slate-700 hover:bg-slate-50 hover:border-slate-300"
            }`}
          >
            <div
              className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${
                isActive
                  ? "bg-white/20 text-white"
                  : "bg-emerald-50 text-emerald-800"
              }`}
            >
              <Icon className="w-5 h-5" />
            </div>

            <div>
              <span
                className={`block text-xs font-bold leading-tight ${
                  isActive ? "text-white" : "text-slate-800"
                }`}
              >
                {m.name}
              </span>
              <span
                className={`block text-[11px] mt-0.5 ${
                  isActive ? "text-emerald-100" : "text-slate-400"
                }`}
              >
                {m.sub}
              </span>
            </div>
          </button>
        );
      })}
    </div>
  );
}
