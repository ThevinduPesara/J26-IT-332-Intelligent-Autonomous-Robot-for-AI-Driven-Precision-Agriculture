import React from "react";

interface HopperCardProps {
  title: string;
  percentage: number;
  statusText: string;
  coverageText: string;
  autoCalibrationStatus: string;
}

export default function HopperCard({
  title,
  percentage,
  statusText,
  coverageText,
  autoCalibrationStatus,
}: HopperCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        <h3 className="text-sm font-bold text-slate-800 mb-4">{title}</h3>

        {/* Gauge & Coverage Details Row */}
        <div className="flex items-center gap-4 mb-4">
          {/* Circular Gauge Representation */}
          <div className="relative w-16 h-16 rounded-full border-4 border-slate-100 flex items-center justify-center shrink-0">
            <svg className="w-full h-full -rotate-90 absolute inset-0" viewBox="0 0 36 36">
              <path
                className="text-emerald-500"
                strokeDasharray={`${percentage}, 100`}
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className="text-xs font-bold text-slate-800">
              {percentage}%
            </span>
          </div>

          <div>
            <h4 className="text-xs md:text-sm font-bold text-slate-800">
              {statusText}
            </h4>
            <p className="text-[11px] text-slate-500 leading-snug mt-0.5">
              {coverageText}
            </p>
          </div>
        </div>
      </div>

      {/* Auto-Calibration Active Badge */}
      <div className="flex justify-between items-center pt-3 border-t border-slate-100 text-xs">
        <span className="text-slate-500 font-medium">Auto-Calibration</span>
        <span className="px-2 py-0.5 rounded-md bg-emerald-100/80 text-emerald-800 font-semibold text-[11px]">
          {autoCalibrationStatus}
        </span>
      </div>
    </div>
  );
}
