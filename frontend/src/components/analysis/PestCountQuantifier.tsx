import React from "react";
import { Bug, AlertOctagon, Target, CheckCircle2 } from "lucide-react";
import { researchModelsData } from "@/data/researchModelsData";
import ModelMediaUploader from "@/components/analysis/ModelMediaUploader";

export default function PestCountQuantifier() {
  const data = researchModelsData.pestCount;

  const pestSamples = [
    {
      label: "Aphid Cluster Leaf Zoom (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Foliage Macro Inspection (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Under-Canopy Micro Camera (Video)",
      type: "video" as const,
      url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    },
  ];

  return (
    <div className="space-y-6">
      {/* 1. Overview Banner */}
      <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <span className="text-xs font-bold tracking-wider text-red-800 uppercase">
            MODEL 4 • PRECISE PEST DENSITY & MULTI-CLASS QUANTIFIER
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 border border-red-200">
            <Bug className="w-3.5 h-3.5" />
            {data.badge}
          </span>
        </div>

        <h2 className="text-lg md:text-xl font-bold text-slate-800 mb-1">
          {data.title}
        </h2>
        <p className="text-xs text-slate-500 mb-4 max-w-3xl">{data.summary}</p>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div>
            Target: <span className="font-bold text-slate-800">{data.scanTarget}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            AI Confidence Avg: <span className="font-bold text-emerald-800">{data.confidenceAvg}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Time: <span className="font-semibold text-slate-500">{data.scanTimestamp}</span>
          </div>
        </div>
      </div>

      {/* 2. Photo & Video Upload / Sample Preview Field */}
      <ModelMediaUploader
        modelName="Precise Pest Counting"
        description="Upload high-magnification leaf photos or micro-camera video streams to calculate exact individual pest numbers and infestation density."
        defaultSamples={pestSamples}
        onAnalyze={(url, type) =>
          alert(`Precise Pest Counter Model executed on ${type.toUpperCase()}: Exactly 64 Pests Counted!`)
        }
      />

      {/* 3. Specific Total Pest Count KPI Card & Species Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
              SPECIFIC NO. OF PESTS DETECTED
            </span>
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-4xl md:text-5xl font-extrabold text-red-600 tracking-tight">
                {data.totalPestCount}
              </span>
              <span className="text-sm font-bold text-slate-500">Insects Counted</span>
            </div>
            <p className="text-xs text-slate-500">
              Exact individual micro-organism count from stereoscopic optical crop zoom.
            </p>
          </div>

          <div className="pt-4 mt-4 border-t border-slate-100">
            <span className="inline-flex items-center gap-1.5 text-xs font-bold text-red-700 bg-red-50 px-2.5 py-1 rounded-md border border-red-200">
              <AlertOctagon className="w-3.5 h-3.5" />
              {data.infestationLevel}
            </span>
          </div>
        </div>

        {/* Pest Species Breakdown Cards */}
        <div className="md:col-span-2 bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800 mb-1">
              Identified Insect Species & Quantities
            </h3>
            <p className="text-xs text-slate-400 mb-5">
              Specific counts categorized by insect classification.
            </p>

            <div className="space-y-4">
              {data.pestBreakdown.map((pest) => (
                <div key={pest.species}>
                  <div className="flex justify-between items-center text-xs mb-1">
                    <span className="font-bold text-slate-800">{pest.species}</span>
                    <span className="font-mono font-bold text-slate-900">
                      {pest.count} pests ({pest.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mb-1">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${pest.color}`}
                      style={{ width: `${pest.percentage}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>{pest.typicalLocation}</span>
                    <span className="font-semibold text-slate-700">{pest.risk}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 4. Recommended Precision Spraying Card */}
      <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider block mb-1">
            TARGETED AUTOMATED SPRAY RECOMMENDATION
          </span>
          <h4 className="text-sm font-bold text-slate-800">
            {data.recommendedSpraying.organicFormulation}
          </h4>
          <p className="text-xs text-slate-600 mt-0.5">
            Dose: <span className="font-bold">{data.recommendedSpraying.targetVolume}</span> • Status:{" "}
            <span className="font-semibold text-emerald-800">{data.recommendedSpraying.status}</span>
          </p>
        </div>

        <button
          onClick={() => alert("Initiating targeted organic precision spraying sequence...")}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-[#14532d] hover:bg-emerald-900 active:scale-98 transition shadow-xs cursor-pointer shrink-0"
        >
          <Target className="w-4 h-4" />
          Trigger Precision Spray
        </button>
      </div>
    </div>
  );
}
