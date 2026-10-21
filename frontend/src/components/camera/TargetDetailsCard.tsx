"use client";

import React from "react";
import { CheckCircle2, Zap, Lock } from "lucide-react";

interface TargetDetailsCardProps {
  target: {
    statusBadge: string;
    plantId: string;
    species: string;
    healthStatus: string;
    aiConfidence: string;
    timestamp: string;
    diagnostics: {
      soilMoisture: string;
      npkIndex: string;
    };
  };
  onTriggerTreatment?: () => void;
}

export default function TargetDetailsCard({
  target,
  onTriggerTreatment = () =>
    alert("Precision Treatment Dispenser Triggered for Target " + target.plantId),
}: TargetDetailsCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between h-full">
      <div>
        {/* Header: Title and Locked Status */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-slate-800">Target Details</h3>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Lock className="w-3 h-3" />
            {target.statusBadge}
          </span>
        </div>

        {/* Target Close-up Preview Card */}
        <div className="relative w-full aspect-4/3 rounded-xl overflow-hidden mb-5 border border-slate-200 shadow-inner group">
          <div
            className="w-full h-full bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?auto=format&fit=crop&w=800&q=80')`,
            }}
          />
          {/* Overlay Tag */}
          <div className="absolute top-2 left-1/2 -translate-x-1/2 text-[10px] font-mono font-medium text-white/90 bg-black/40 px-2 py-0.5 rounded-full backdrop-blur-xs">
            10:09 AM
          </div>

          <div className="absolute inset-x-0 bottom-3 flex flex-col items-center">
            <span className="text-[11px] text-white/80 font-medium mb-1 drop-shadow-sm">
              Tap to focus
            </span>
            <div className="w-8 h-8 rounded-full bg-white/90 shadow-md flex items-center justify-center text-amber-500">
              <Zap className="w-4 h-4 fill-amber-500" />
            </div>
          </div>
        </div>

        {/* Plant Metadata Properties */}
        <div className="space-y-2.5 text-xs">
          <div className="flex justify-between items-center py-1 border-b border-slate-100">
            <span className="text-slate-400 font-medium">Plant ID</span>
            <span className="font-bold text-slate-800">{target.plantId}</span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-slate-100">
            <span className="text-slate-400 font-medium">Species</span>
            <span className="font-semibold text-slate-700 italic">
              {target.species}
            </span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-slate-100">
            <span className="text-slate-400 font-medium">Health Status</span>
            <span className="inline-flex items-center gap-1 font-semibold text-emerald-700">
              <CheckCircle2 className="w-3.5 h-3.5" />
              {target.healthStatus}
            </span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-slate-100">
            <span className="text-slate-400 font-medium">AI Confidence</span>
            <span className="font-bold text-slate-800">{target.aiConfidence}</span>
          </div>

          <div className="flex justify-between items-center py-1">
            <span className="text-slate-400 font-medium">Timestamp</span>
            <span className="font-mono text-slate-600">{target.timestamp}</span>
          </div>
        </div>

        {/* Telemetry Diagnostics Section */}
        <div className="mt-5 pt-4 border-t border-slate-100">
          <span className="block text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-2">
            TELEMETRY DIAGNOSTICS
          </span>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Soil Moisture</span>
              <span className="font-medium text-slate-800">
                {target.diagnostics.soilMoisture}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">NPK Index</span>
              <span className="font-mono font-medium text-slate-800">
                {target.diagnostics.npkIndex}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Button: Trigger Precision Treatment */}
      <div className="mt-6 pt-2">
        <button
          onClick={onTriggerTreatment}
          className="w-full inline-flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-sm font-semibold text-white bg-[#14532d] hover:bg-emerald-900 active:scale-[0.98] transition shadow-xs cursor-pointer"
        >
          <Zap className="w-4 h-4 fill-white" />
          Trigger Precision Treatment
        </button>
      </div>
    </div>
  );
}
