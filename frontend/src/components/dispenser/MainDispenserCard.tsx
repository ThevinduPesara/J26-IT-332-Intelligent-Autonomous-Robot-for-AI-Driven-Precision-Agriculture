"use client";

import React, { useState } from "react";
import { Tractor, Power, ArrowRight } from "lucide-react";

interface MetricItem {
  id: string;
  label: string;
  value: string;
  statusTag?: string;
}

interface MainDispenserCardProps {
  title: string;
  unitId: string;
  hopperCap: string;
  statusBadge: string;
  metrics: MetricItem[];
  actuationTitle: string;
  actuationDescription: string;
  initialState?: boolean;
}

export default function MainDispenserCard({
  title,
  unitId,
  hopperCap,
  statusBadge,
  metrics,
  actuationTitle,
  actuationDescription,
  initialState = false,
}: MainDispenserCardProps) {
  const [isActive, setIsActive] = useState(initialState);

  const toggleDispenser = () => {
    setIsActive((prev) => !prev);
  };

  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col gap-6">
      {/* Top Banner: Tractor Icon, Title, and Unit ID */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-emerald-100/70 text-emerald-800 flex items-center justify-center shrink-0">
            <Tractor className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base md:text-lg font-bold text-slate-800">
              {title}
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Unit ID: <span className="font-semibold text-slate-700">{unitId}</span> • Hopper Cap:{" "}
              <span className="font-semibold text-slate-700">{hopperCap}</span>
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
            isActive
              ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
              : "bg-slate-100 text-slate-600 border border-slate-200"
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isActive ? "bg-emerald-600 animate-ping" : "bg-slate-400"
            }`}
          />
          {isActive ? "Active Dispensing" : statusBadge}
        </span>
      </div>

      {/* 3 Metric Mini Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        {metrics.map((m) => (
          <div
            key={m.id}
            className="p-4 rounded-xl bg-slate-50/80 border border-slate-100 flex flex-col justify-between"
          >
            <span className="text-xs font-medium text-slate-400 mb-1">
              {m.label}
            </span>
            <div className="flex items-baseline gap-2 flex-wrap">
              <span className="text-base md:text-lg font-bold text-slate-800">
                {m.value}
              </span>
              {m.statusTag && (
                <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700">
                  <ArrowRight className="w-3 h-3 mr-0.5 inline" />
                  {m.statusTag}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Master Hardware Actuation Control Container */}
      <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-800">
            {actuationTitle}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {actuationDescription}
          </p>
        </div>

        {/* Big Hardware Toggle Button */}
        <button
          onClick={toggleDispenser}
          className={`inline-flex items-center justify-center gap-2.5 px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200 active:scale-98 cursor-pointer shrink-0 ${
            isActive
              ? "bg-red-700 hover:bg-red-800 text-white shadow-md shadow-red-700/20"
              : "bg-[#14532d] hover:bg-emerald-900 text-white shadow-md shadow-emerald-950/20"
          }`}
        >
          <Power className="w-4 h-4" />
          {isActive ? "Turn OFF Dispenser" : "Turn ON Dispenser"}
        </button>
      </div>
    </div>
  );
}
