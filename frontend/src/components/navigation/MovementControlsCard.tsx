"use client";

import React from "react";
import { SlidersHorizontal, ArrowLeft, ArrowRight, Home, OctagonX } from "lucide-react";

interface MovementControlsCardProps {
  title: string;
  description: string;
  statusState: string;
  emergencyNotice: string;
  onMoveLeft: () => void;
  onMoveRight: () => void;
  onReturnHome: () => void;
  onEmergencyStop: () => void;
}

export default function MovementControlsCard({
  title,
  description,
  statusState,
  emergencyNotice,
  onMoveLeft,
  onMoveRight,
  onReturnHome,
  onEmergencyStop,
}: MovementControlsCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between h-full">
      <div>
        {/* Header: Title and Icon */}
        <div className="flex items-center justify-between gap-2 mb-2">
          <h2 className="text-base font-bold text-slate-800">{title}</h2>
          <SlidersHorizontal className="w-5 h-5 text-slate-500" />
        </div>
        <p className="text-xs text-slate-500 leading-relaxed mb-6">
          {description}
        </p>

        {/* Status State Box */}
        <div className="bg-slate-50/80 rounded-xl p-4 text-center border border-slate-100 mb-6">
          <span className="block text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1">
            Status State
          </span>
          <span className="text-lg font-bold text-emerald-700">
            {statusState}
          </span>
        </div>

        {/* Move Left & Move Right Action Buttons */}
        <div className="grid grid-cols-2 gap-3.5 mb-3.5">
          <button
            type="button"
            onClick={onMoveLeft}
            onMouseDown={onMoveLeft}
            className="flex flex-col items-center justify-center gap-1.5 py-4 px-3 rounded-xl bg-[#14532d] hover:bg-emerald-900 active:bg-emerald-950 text-white font-semibold text-xs active:scale-95 transition shadow-xs cursor-pointer select-none"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-bold">Move Left</span>
            <span className="text-[10px] text-emerald-200/80 font-normal">Click or Hold</span>
          </button>

          <button
            type="button"
            onClick={onMoveRight}
            onMouseDown={onMoveRight}
            className="flex flex-col items-center justify-center gap-1.5 py-4 px-3 rounded-xl bg-[#14532d] hover:bg-emerald-900 active:bg-emerald-950 text-white font-semibold text-xs active:scale-95 transition shadow-xs cursor-pointer select-none"
          >
            <ArrowRight className="w-5 h-5" />
            <span className="font-bold">Move Right</span>
            <span className="text-[10px] text-emerald-200/80 font-normal">Click or Hold</span>
          </button>
        </div>

        {/* Home / Return to Start (0m) Button */}
        <button
          onClick={onReturnHome}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-indigo-50/80 hover:bg-indigo-100 text-slate-700 font-semibold text-xs border border-indigo-100 active:scale-98 transition cursor-pointer mb-6"
        >
          <Home className="w-4 h-4 text-slate-600" />
          <span>Home / Return to Start (0m)</span>
        </button>
      </div>

      {/* STOP ROBOT Button & Emergency brake notice */}
      <div>
        <button
          onClick={onEmergencyStop}
          className="w-full flex items-center justify-center gap-2 py-3.5 px-4 rounded-xl bg-[#b91c1c] hover:bg-red-800 text-white font-bold text-sm shadow-md shadow-red-700/20 active:scale-98 transition cursor-pointer"
        >
          <OctagonX className="w-4 h-4" />
          <span>STOP ROBOT</span>
        </button>
        <span className="block text-center text-[11px] text-slate-400 mt-2 font-medium">
          {emergencyNotice}
        </span>
      </div>
    </div>
  );
}
