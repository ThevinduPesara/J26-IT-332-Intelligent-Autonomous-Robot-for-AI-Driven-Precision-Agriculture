"use client";

import React from "react";
import { Bot } from "lucide-react";

interface CableTrackProps {
  title: string;
  spanText: string;
  statusText: string;
  currentPosition: number; // e.g. 45.2
  totalLength: number; // e.g. 100
  winchSpeed: string;
  tensionLoad: string;
  motorTemp: string;
}

export default function CableTrack({
  title,
  spanText,
  statusText,
  currentPosition,
  totalLength,
  winchSpeed,
  tensionLoad,
  motorTemp,
}: CableTrackProps) {
  // Calculate percentage along the 100m track
  const progressPercent = Math.min(
    Math.max((currentPosition / totalLength) * 100, 0),
    100
  );

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      {/* Top Header */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
          <h3 className="text-base font-bold text-slate-800">{title}</h3>
          <span className="text-xs font-medium text-slate-500">
            Track Status:{" "}
            <span className="font-semibold text-emerald-700">{statusText}</span>
          </span>
        </div>
        <p className="text-xs text-slate-400 mb-8">{spanText}</p>

        {/* Cable Visualization Track */}
        <div className="relative w-full py-8 px-4 bg-slate-50/70 rounded-xl border border-slate-100 my-2">
          {/* Background Wire / Track Line */}
          <div className="w-full h-1.5 bg-slate-200 rounded-full relative">
            {/* Active Traveled Distance Line */}
            <div
              className="h-full bg-emerald-600 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Waypoint Markers (0m, 25m, 50m, 75m, 100m) */}
          <div className="absolute inset-x-4 top-1/2 -translate-y-1/2 flex justify-between pointer-events-none">
            {/* 0m */}
            <div className="relative flex flex-col items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-700 border-2 border-white shadow-xs" />
              <span className="absolute top-4 text-[10px] font-semibold text-slate-400 whitespace-nowrap">
                0m (Start)
              </span>
            </div>

            {/* 25m */}
            <div className="relative flex flex-col items-center">
              <span className="w-3 h-3 rounded-full bg-white border-2 border-slate-300 shadow-xs" />
              <span className="absolute top-4 text-[10px] font-semibold text-slate-400 whitespace-nowrap">
                25m
              </span>
            </div>

            {/* 50m */}
            <div className="relative flex flex-col items-center">
              <span className="w-3 h-3 rounded-full bg-white border-2 border-slate-300 shadow-xs" />
              <span className="absolute top-4 text-[10px] font-semibold text-slate-400 whitespace-nowrap">
                50m
              </span>
            </div>

            {/* 75m */}
            <div className="relative flex flex-col items-center">
              <span className="w-3 h-3 rounded-full bg-white border-2 border-slate-300 shadow-xs" />
              <span className="absolute top-4 text-[10px] font-semibold text-slate-400 whitespace-nowrap">
                75m
              </span>
            </div>

            {/* 100m */}
            <div className="relative flex flex-col items-center">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-400 border-2 border-white shadow-xs" />
              <span className="absolute top-4 text-[10px] font-semibold text-slate-400 whitespace-nowrap">
                100m (End)
              </span>
            </div>
          </div>

          {/* Current Robot Position Pin Indicator */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 transition-all duration-500 flex flex-col items-center z-10"
            style={{ left: `calc(1rem + (100% - 2rem) * (${progressPercent} / 100))` }}
          >
            {/* Tooltip Badge */}
            <div className="mb-1.5 px-2 py-0.5 rounded-md bg-emerald-900 text-white text-[10px] font-mono font-semibold tracking-wide shadow-sm whitespace-nowrap">
              Robot @ {currentPosition}m
            </div>

            {/* Robot Circle Node */}
            <div className="w-6 h-6 rounded-full bg-emerald-800 text-white flex items-center justify-center border-2 border-white shadow-md">
              <Bot className="w-3.5 h-3.5" />
            </div>
          </div>
        </div>
      </div>

      {/* Telemetry Metric Footer */}
      <div className="grid grid-cols-3 gap-2 pt-6 mt-4 border-t border-slate-100 text-center">
        <div>
          <span className="block text-[11px] font-medium text-slate-400">
            Winch Speed
          </span>
          <span className="text-xs md:text-sm font-semibold text-slate-700">
            {winchSpeed}
          </span>
        </div>
        <div>
          <span className="block text-[11px] font-medium text-slate-400">
            Tension Load
          </span>
          <span className="text-xs md:text-sm font-semibold text-slate-700">
            {tensionLoad}
          </span>
        </div>
        <div>
          <span className="block text-[11px] font-medium text-slate-400">
            Motor Temp
          </span>
          <span className="text-xs md:text-sm font-semibold text-slate-700">
            {motorTemp}
          </span>
        </div>
      </div>
    </div>
  );
}
