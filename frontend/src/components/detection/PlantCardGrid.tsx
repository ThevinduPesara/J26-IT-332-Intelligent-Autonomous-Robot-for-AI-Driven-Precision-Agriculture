"use client";

import React from "react";
import { ArrowRight } from "lucide-react";

export interface PlantCardItem {
  id: string;
  status: "Healthy" | "Moderate" | "Poor" | string;
  confidence: string;
  species: string;
  zone: string;
  description: string;
  scannedTime: string;
  imageUrl: string;
}

interface PlantCardGridProps {
  plants: PlantCardItem[];
}

export default function PlantCardGrid({ plants }: PlantCardGridProps) {
  const getBadgeConfig = (status: string, confidence: string) => {
    switch (status) {
      case "Healthy":
        return {
          bg: "bg-emerald-600/90 text-white",
          dot: "bg-white",
          text: `Healthy (${confidence})`,
        };
      case "Moderate":
        return {
          bg: "bg-amber-600/90 text-white",
          dot: "bg-white",
          text: `Moderate (${confidence})`,
        };
      case "Poor":
        return {
          bg: "bg-red-600/90 text-white",
          dot: "bg-white",
          text: `Poor (${confidence})`,
        };
      default:
        return {
          bg: "bg-slate-700/90 text-white",
          dot: "bg-white",
          text: `${status} (${confidence})`,
        };
    }
  };

  if (plants.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-12 text-center border border-slate-200/80 shadow-xs">
        <p className="text-sm text-slate-500 font-medium">
          No plant records match your search or filter criteria.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {plants.map((plant) => {
        const badge = getBadgeConfig(plant.status, plant.confidence);

        return (
          <div
            key={plant.id}
            className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col justify-between group hover:shadow-md transition-shadow"
          >
            {/* Top: Plant Image Container */}
            <div className="relative w-full aspect-16/10 bg-slate-900 overflow-hidden">
              <div
                className="w-full h-full bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
                style={{ backgroundImage: `url('${plant.imageUrl}')` }}
              />

              {/* Top-Right Status Badge */}
              <div className="absolute top-3 right-3">
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold backdrop-blur-xs shadow-sm ${badge.bg}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
                  {badge.text}
                </span>
              </div>

              {/* Bottom-Left Plant ID Pill */}
              <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold text-white/90 border border-white/10">
                #{plant.id}
              </div>
            </div>

            {/* Middle: Content & Metadata */}
            <div className="p-5 flex-1 flex flex-col justify-between">
              <div>
                <div className="flex items-baseline justify-between gap-2 mb-2">
                  <h4 className="text-sm font-bold text-slate-800 leading-tight">
                    {plant.species}
                  </h4>
                  <span className="text-[11px] font-semibold text-slate-400 shrink-0">
                    {plant.zone}
                  </span>
                </div>

                <p className="text-xs text-slate-500 leading-relaxed line-clamp-2 mb-4">
                  {plant.description}
                </p>
              </div>

              {/* Bottom row: Scanned Time and Details Button */}
              <div className="flex items-center justify-between text-xs pt-3 border-t border-slate-100">
                <span className="text-slate-400 font-medium">
                  Scanned: {plant.scannedTime}
                </span>

                <button
                  onClick={() => alert(`Showing diagnosis details for #${plant.id}`)}
                  className="inline-flex items-center gap-1 font-semibold text-emerald-700 hover:text-emerald-900 transition cursor-pointer"
                >
                  Details
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
