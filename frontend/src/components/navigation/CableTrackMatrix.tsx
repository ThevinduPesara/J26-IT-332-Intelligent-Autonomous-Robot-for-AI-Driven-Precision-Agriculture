"use client";

import React from "react";
import { Bot, GitCommitVertical } from "lucide-react";

interface TrackNode {
  label: string;
  position: number;
}

interface CableTrackMatrixProps {
  title: string;
  speed: string;
  movementState: string;
  currentPosition: number;
  totalLength: number;
  targetNode: string;
  nodes: TrackNode[];
}

export default function CableTrackMatrix({
  title,
  speed,
  movementState,
  currentPosition,
  totalLength,
  targetNode,
  nodes,
}: CableTrackMatrixProps) {
  // Percentage along the track
  const progressPercent = Math.min(
    Math.max((currentPosition / totalLength) * 100, 0),
    100
  );

  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        {/* Top Header: Title, Speed & Movement Status Badges */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-8">
          <div className="flex items-center gap-2.5">
            <GitCommitVertical className="w-5 h-5 text-slate-700" />
            <h2 className="text-base md:text-lg font-bold text-slate-800">
              {title}
            </h2>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold">
            <span className="px-3 py-1 rounded-lg bg-slate-100 text-slate-700 border border-slate-200">
              Speed: <span className="font-bold">{speed}</span>
            </span>
            <span
              className={`px-3 py-1 rounded-lg border ${
                movementState === "Stopped"
                  ? "bg-emerald-100/80 text-emerald-800 border-emerald-200"
                  : "bg-teal-100 text-teal-800 border-teal-200"
              }`}
            >
              {movementState}
            </span>
          </div>
        </div>

        {/* 100m Horizontal Cable Track Slider Visualization */}
        <div className="relative w-full py-10 px-6 bg-slate-50/80 rounded-2xl border border-slate-100 my-4">
          {/* Main Track Cable Line */}
          <div className="w-full h-2.5 bg-slate-200 rounded-full relative">
            {/* Traveled Distance Line */}
            <div
              className="h-full bg-emerald-800 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          {/* Node Markers: 0m, 20m, 40m, 60m, 80m, 100m */}
          <div className="absolute inset-x-6 top-1/2 -translate-y-1/2 flex justify-between pointer-events-none">
            {nodes.map((node) => (
              <div key={node.label} className="relative flex flex-col items-center">
                <span
                  className={`w-3.5 h-3.5 rounded-full border-2 border-white shadow-xs ${
                    node.position <= currentPosition
                      ? "bg-emerald-800"
                      : "bg-slate-300"
                  }`}
                />
                <span className="absolute top-5 text-[11px] font-semibold text-slate-400 whitespace-nowrap">
                  {node.label}
                </span>
              </div>
            ))}
          </div>

          {/* Moving Robot Pin Node Indicator */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 transition-all duration-300 flex flex-col items-center z-10"
            style={{
              left: `calc(1.5rem + (100% - 3rem) * (${progressPercent} / 100))`,
            }}
          >
            {/* Tooltip Badge */}
            <div className="mb-2 px-2.5 py-0.5 rounded-md bg-emerald-950 text-white text-[11px] font-mono font-semibold tracking-wide shadow-md whitespace-nowrap">
              {currentPosition.toFixed(1)}m
            </div>

            {/* Robot Center Circle */}
            <div className="w-8 h-8 rounded-full bg-[#18533a] text-white flex items-center justify-center border-2 border-white shadow-lg">
              <Bot className="w-4 h-4" />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Telemetry: Progress bar, Current Position, and Target Node */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 mt-6 border-t border-slate-100">
        <div>
          <div className="flex justify-between items-center text-xs mb-1.5">
            <span className="text-slate-400 font-medium">Navigation Progress</span>
            <span className="font-bold text-slate-800">{progressPercent.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="bg-emerald-800 h-full rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        <div className="sm:text-center">
          <span className="block text-xs font-medium text-slate-400 mb-0.5">
            Current Position
          </span>
          <span className="text-base font-bold text-emerald-800">
            {currentPosition.toFixed(2)} m
          </span>
        </div>

        <div className="sm:text-right">
          <span className="block text-xs font-medium text-slate-400 mb-0.5">
            Target Node
          </span>
          <span className="text-sm font-bold text-slate-800">{targetNode}</span>
        </div>
      </div>
    </div>
  );
}
