import React from "react";
import { Network } from "lucide-react";

interface DispenserHeaderProps {
  title: string;
  description: string;
  protocol: {
    label: string;
    value: string;
  };
}

export default function DispenserHeader({
  title,
  description,
  protocol,
}: DispenserHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
      {/* Left: Title & Subtitle */}
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">
          {title}
        </h1>
        <p className="text-xs md:text-sm text-slate-500 mt-1 max-w-2xl">
          {description}
        </p>
      </div>

      {/* Right: Hardware Protocol Badge Card */}
      <div className="bg-[#e0e7ff]/70 border border-indigo-100 rounded-2xl p-4 flex items-center gap-3 shrink-0">
        <div className="w-10 h-10 rounded-xl bg-teal-800 text-white flex items-center justify-center shrink-0 shadow-xs">
          <Network className="w-5 h-5" />
        </div>
        <div>
          <span className="block text-[11px] font-semibold text-slate-500">
            {protocol.label}
          </span>
          <span className="text-sm font-bold text-slate-800">
            {protocol.value}
          </span>
        </div>
      </div>
    </div>
  );
}
