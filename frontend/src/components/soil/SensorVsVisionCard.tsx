import React from "react";
import { Info, ShieldCheck } from "lucide-react";

interface SensorVsVisionCardProps {
  title: string;
  paragraph1: string;
  paragraph2: string;
  calibratedBadge: string;
}

export default function SensorVsVisionCard({
  title,
  paragraph1,
  paragraph2,
  calibratedBadge,
}: SensorVsVisionCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs flex flex-col justify-between h-full">
      <div>
        {/* Info Icon & Title */}
        <div className="w-10 h-10 rounded-xl bg-emerald-100/80 text-emerald-800 flex items-center justify-center mb-4">
          <Info className="w-5 h-5" />
        </div>

        <h3 className="text-base font-bold text-slate-800 mb-3">
          {title}
        </h3>

        {/* Informational Paragraphs */}
        <div className="space-y-3 text-xs text-slate-500 leading-relaxed">
          <p>{paragraph1}</p>
          <p>
            These telemetry values are{" "}
            <span className="font-bold text-slate-700">entirely separate</span>{" "}
            from AI visual plant analysis, which assesses foliage discoloration
            and canopy stress optically via the top-mounted stereoscopic camera.
          </p>
        </div>
      </div>

      {/* Verification Badge */}
      <div className="pt-6 mt-4 border-t border-slate-100">
        <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
          <span>{calibratedBadge}</span>
        </div>
      </div>
    </div>
  );
}
