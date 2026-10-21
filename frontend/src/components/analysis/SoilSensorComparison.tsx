"use client";

import React, { useState } from "react";
import { Scale, RefreshCw, Send, CheckCircle2 } from "lucide-react";
import { researchModelsData } from "@/data/researchModelsData";

export default function SoilSensorComparison() {
  const data = researchModelsData.soilComparison;
  const [dispensed, setDispensed] = useState(false);

  const handleDispense = () => {
    setDispensed(true);
    alert(
      "Precision Fertilizer Dosage command transmitted to AgriBot Dispenser Node via MQTT!"
    );
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <span className="text-xs font-bold tracking-wider text-teal-800 uppercase">
            MODEL 2 • SENSOR VS. TARGET DEFICIENCY CALCULATOR
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-teal-100 text-teal-800 border border-teal-200">
            <Scale className="w-3.5 h-3.5" />
            {data.badge}
          </span>
        </div>

        <h2 className="text-lg md:text-xl font-bold text-slate-800 mb-1">
          {data.title}
        </h2>
        <p className="text-xs text-slate-500 mb-4 max-w-3xl">{data.summary}</p>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div>
            Probe Hardware:{" "}
            <span className="font-mono font-bold text-slate-800">
              {data.probeId}
            </span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Last Probed:{" "}
            <span className="font-semibold text-slate-700">
              {data.lastReadingTime}
            </span>
          </div>
        </div>
      </div>

      {/* Comparison Analysis Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-slate-800">
              Sensor vs Model Target Comparison & Dosage Computation
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live electrochemical sensor values matched against Chilli crop stage demands.
            </p>
          </div>

          <button
            onClick={handleDispense}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-[#0f5132] hover:bg-emerald-900 active:scale-98 transition cursor-pointer shadow-xs"
          >
            <Send className="w-3.5 h-3.5" />
            Dispense Recommended Dosage
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/50 text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
                <th className="py-3.5 px-6">NUTRIENT</th>
                <th className="py-3.5 px-6">PROBED VALUE</th>
                <th className="py-3.5 px-6">TARGET NEED</th>
                <th className="py-3.5 px-6">DEFICIT / GAP</th>
                <th className="py-3.5 px-6">STATUS</th>
                <th className="py-3.5 px-6">RECOMMENDED DOSAGE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data.comparisonTable.map((row) => (
                <tr key={row.nutrient} className="hover:bg-slate-50/60 transition">
                  <td className="py-4 px-6 font-bold text-slate-800">
                    {row.nutrient}
                  </td>
                  <td className="py-4 px-6 font-mono font-bold text-slate-700">
                    {row.currentReading} {row.unit}
                  </td>
                  <td className="py-4 px-6 font-mono font-bold text-emerald-800">
                    {row.requiredTarget} {row.unit}
                  </td>
                  <td className="py-4 px-6 font-mono font-bold text-red-600">
                    +{row.deficit} {row.unit}
                  </td>
                  <td className="py-4 px-6">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded-md text-[11px] font-bold ${row.statusColor}`}
                    >
                      {row.status}
                    </span>
                  </td>
                  <td className="py-4 px-6 font-semibold text-slate-800">
                    {row.recommendedDose}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
