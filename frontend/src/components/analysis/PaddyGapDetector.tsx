import React from "react";
import { Grid, AlertTriangle, Layers, Navigation } from "lucide-react";
import { researchModelsData } from "@/data/researchModelsData";
import ModelMediaUploader from "@/components/analysis/ModelMediaUploader";

export default function PaddyGapDetector() {
  const data = researchModelsData.paddyGap;

  const paddySamples = [
    {
      label: "Drone Aerial View (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Row Discontinuity Grid (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Paddy Field Flyover (Video)",
      type: "video" as const,
      url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    },
  ];

  return (
    <div className="space-y-6">
      {/* 1. Overview Banner */}
      <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <span className="text-xs font-bold tracking-wider text-emerald-800 uppercase">
            MODEL 3 • PADDY CROP CONTINUITY & GAP DETECTION
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Grid className="w-3.5 h-3.5" />
            {data.badge}
          </span>
        </div>

        <h2 className="text-lg md:text-xl font-bold text-slate-800 mb-1">
          {data.title}
        </h2>
        <p className="text-xs text-slate-500 mb-4 max-w-3xl">{data.summary}</p>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div>
            Target Field: <span className="font-bold text-slate-800">{data.cropType}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Coverage: <span className="font-semibold text-slate-700">{data.fieldCoverage}</span>
          </div>
        </div>
      </div>

      {/* 2. Photo & Video Upload / Sample Preview Field */}
      <ModelMediaUploader
        modelName="Paddy Gap Detection"
        description="Upload aerial drone videos or multispectral photos to detect missing seedlings, crop gaps, and auto-queue reseeding points."
        defaultSamples={paddySamples}
        onAnalyze={(url, type) =>
          alert(`Paddy Gap Detection Model executed on ${type.toUpperCase()}: 28 Gaps Mapped!`)
        }
      />

      {/* 3. KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs">
          <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            CANOPY GAPS DETECTED
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-amber-600">
              {data.totalGapsDetected}
            </span>
            <span className="text-xs font-semibold text-slate-400">Total Discontinuities</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Seedling gaps exceeding 0.5m spacing threshold.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs">
          <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            MISSING PLANT RATIO
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-800">
              {data.missingPlantPercentage}
            </span>
            <span className="text-xs font-semibold text-emerald-700">Canopy Loss</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Projected 4.2% yield drop if gaps remain unseeded.
          </p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs">
          <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
            AUTOMATED ACTION
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-emerald-800">
              Auto-Reseed Ready
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Coordinates linked to pneumatic seed dispenser.
          </p>
        </div>
      </div>

      {/* 4. Detected Gaps Location Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800">
              Identified Crop Gap Waypoints & Coordinates
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Specific row coordinates queued for precision robot drop.
            </p>
          </div>
          <Navigation className="w-4 h-4 text-slate-400" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/50 text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
                <th className="py-3.5 px-6">GAP ID</th>
                <th className="py-3.5 px-6">ROW LOCATION</th>
                <th className="py-3.5 px-6">DISCONTINUITY SPAN</th>
                <th className="py-3.5 px-6">FIELD COORDINATES</th>
                <th className="py-3.5 px-6">RESEED PRIORITY</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data.gapLocations.map((gap) => (
                <tr key={gap.id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 px-6 font-mono font-bold text-slate-800">{gap.id}</td>
                  <td className="py-3.5 px-6 font-semibold text-slate-700">{gap.row}</td>
                  <td className="py-3.5 px-6 font-medium text-slate-800">{gap.span}</td>
                  <td className="py-3.5 px-6 font-mono text-slate-600">{gap.coords}</td>
                  <td className="py-3.5 px-6">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded-md text-[11px] font-bold ${
                        gap.priority === "High"
                          ? "bg-red-100 text-red-800"
                          : gap.priority === "Medium"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {gap.priority}
                    </span>
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
