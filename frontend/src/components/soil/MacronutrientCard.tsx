import React from "react";
import { Clock } from "lucide-react";

interface MacronutrientCardProps {
  category: string;
  name: string;
  symbol: string;
  value: string;
  unit: string;
  rangeText: string;
  percentage: number;
  status: string;
  statusType: "optimal" | "moderate";
  updatedTime: string;
  targetRange: string;
  barColor: string;
}

export default function MacronutrientCard({
  category,
  name,
  symbol,
  value,
  unit,
  rangeText,
  percentage,
  status,
  statusType,
  updatedTime,
  targetRange,
  barColor,
}: MacronutrientCardProps) {
  const isOptimal = statusType === "optimal";

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        {/* Top Header: Category, Name & Status Badge */}
        <div className="flex items-start justify-between gap-2 mb-4">
          <div>
            <span className="block text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              {category}
            </span>
            <h2 className="text-base font-bold text-slate-800">
              {name} <span className="text-slate-400 font-normal">{symbol}</span>
            </h2>
          </div>

          <span
            className={`px-2.5 py-0.5 rounded-md text-xs font-semibold ${
              isOptimal
                ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                : "bg-amber-100 text-amber-900 border border-amber-200"
            }`}
          >
            {status}
          </span>
        </div>

        {/* Big Value Display */}
        <div className="flex items-baseline gap-1.5 mb-4">
          <span className="text-3xl md:text-4xl font-extrabold text-slate-800 tracking-tight">
            {value}
          </span>
          <span className="text-xs font-semibold text-slate-400">{unit}</span>
        </div>

        {/* Range Label & Percentage */}
        <div className="flex justify-between items-center text-xs text-slate-400 mb-1.5 font-medium">
          <span>{rangeText}</span>
          <span className="font-semibold text-slate-600">{percentage}%</span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mb-6">
          <div
            className={`h-full rounded-full transition-all duration-500 ${barColor}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Footer: Updated Time & Target Range */}
      <div className="flex items-center justify-between text-xs pt-4 border-t border-slate-100">
        <div className="flex items-center gap-1.5 text-slate-400">
          <Clock className="w-3.5 h-3.5" />
          <span>Updated: {updatedTime}</span>
        </div>
        <span
          className={`font-semibold ${
            isOptimal ? "text-emerald-700" : "text-amber-800"
          }`}
        >
          Target: {targetRange}
        </span>
      </div>
    </div>
  );
}
