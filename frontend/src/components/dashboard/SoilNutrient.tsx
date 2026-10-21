import React from "react";

interface Nutrient {
  name: string;
  value: number;
  max: number;
  unit: string;
  color: string;
}

interface SoilNutrientProps {
  statusBadge: string;
  nutrients: Nutrient[];
}

export default function SoilNutrient({
  statusBadge,
  nutrients,
}: SoilNutrientProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          SOIL NUTRIENT SENSOR
        </span>
        <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100">
          {statusBadge}
        </span>
      </div>

      {/* Nutrient Progress Bars */}
      <div className="space-y-4">
        {nutrients.map((item) => {
          const percentage = Math.min((item.value / item.max) * 100, 100);

          return (
            <div key={item.name}>
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="font-semibold text-slate-700">{item.name}</span>
                <span className="font-bold text-slate-800">
                  {item.value} {item.unit}
                </span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${item.color}`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
