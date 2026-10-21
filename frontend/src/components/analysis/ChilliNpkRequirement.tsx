import React from "react";
import { Sprout, CheckCircle2, Calendar } from "lucide-react";
import { researchModelsData } from "@/data/researchModelsData";
import ModelMediaUploader from "@/components/analysis/ModelMediaUploader";

export default function ChilliNpkRequirement() {
  const data = researchModelsData.chilliRequirement;

  const chilliSamples = [
    {
      label: "Flowering Canopy (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Leaf Chlorosis Zoom (Photo)",
      type: "image" as const,
      url: "https://images.unsplash.com/photo-1592417817098-8f3d6eb228cc?auto=format&fit=crop&w=1000&q=80",
    },
    {
      label: "Robotic Field Inspection (Video)",
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
            MODEL 1 • CHILLI PHENOLOGY PREDICTION
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
            <Sprout className="w-3.5 h-3.5" />
            {data.badge}
          </span>
        </div>

        <h2 className="text-lg md:text-xl font-bold text-slate-800 mb-1">
          {data.title}
        </h2>
        <p className="text-xs text-slate-500 mb-4 max-w-3xl">
          {data.summary}
        </p>

        <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <div>
            Current Crop Stage:{" "}
            <span className="font-bold text-emerald-800">{data.cropStage}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div>
            Target Crop: <span className="font-semibold italic text-slate-700">{data.targetSpecies}</span>
          </div>
        </div>
      </div>

      {/* 2. Photo & Video Upload / Sample Preview Field */}
      <ModelMediaUploader
        modelName="Chilli NPK Prediction"
        description="Upload or choose a canopy photo / video stream to detect vegetative chlorosis and compute dynamic NPK ratios."
        defaultSamples={chilliSamples}
        onAnalyze={(url, type) =>
          alert(`Chilli NPK Model executed on ${type.toUpperCase()}: Analysis verified!`)
        }
      />

      {/* 3. Target Requirements Cards (N, P, K) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {data.requirements.map((req) => (
          <div
            key={req.element}
            className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between"
          >
            <div>
              <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                PREDICTED TARGET DEMAND
              </span>
              <h3 className={`text-base font-bold ${req.color} mb-3`}>
                {req.element}
              </h3>

              <div className="flex items-baseline gap-2 mb-3">
                <span className="text-3xl md:text-4xl font-extrabold text-slate-800 tracking-tight">
                  {req.target}
                </span>
                <span className="text-xs font-semibold text-slate-400">
                  {req.unit}
                </span>
              </div>

              <p className="text-xs text-slate-500 leading-relaxed mb-4">
                {req.importance}
              </p>
            </div>

            <div className={`p-3 rounded-xl ${req.bg} text-[11px] font-semibold ${req.color} flex items-center gap-1.5`}>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Optimal flowering formulation computed</span>
            </div>
          </div>
        ))}
      </div>

      {/* 4. Growth Stages Timeline Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-800">
              Chilli Phenological Stage NPK Demand Matrix
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Standard fertilizer demand profiles across development lifecycle.
            </p>
          </div>
          <Calendar className="w-4 h-4 text-slate-400" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/50 text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
                <th className="py-3.5 px-6">STAGE</th>
                <th className="py-3.5 px-6">NITROGEN (N)</th>
                <th className="py-3.5 px-6">PHOSPHORUS (P)</th>
                <th className="py-3.5 px-6">POTASSIUM (K)</th>
                <th className="py-3.5 px-6">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {data.growthStages.map((stage) => (
                <tr
                  key={stage.stage}
                  className={`transition ${
                    stage.active ? "bg-emerald-50/50 font-semibold" : "hover:bg-slate-50/60"
                  }`}
                >
                  <td className="py-3.5 px-6 text-slate-800">{stage.stage}</td>
                  <td className="py-3.5 px-6 font-mono">{stage.n}</td>
                  <td className="py-3.5 px-6 font-mono">{stage.p}</td>
                  <td className="py-3.5 px-6 font-mono">{stage.k}</td>
                  <td className="py-3.5 px-6">
                    {stage.active ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[11px] font-bold">
                        Current Active Phase
                      </span>
                    ) : (
                      <span className="text-slate-400 text-[11px]">Completed / Upcoming</span>
                    )}
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
