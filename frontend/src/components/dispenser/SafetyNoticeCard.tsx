import React from "react";
import { AlertTriangle } from "lucide-react";

interface SafetyNoticeCardProps {
  title: string;
  description: string;
}

export default function SafetyNoticeCard({
  title,
  description,
}: SafetyNoticeCardProps) {
  return (
    <div className="rounded-2xl p-6 bg-[#fff7ed] border border-orange-200/80 shadow-2xs flex items-start gap-4">
      {/* Alert Warning Icon */}
      <div className="w-9 h-9 rounded-xl bg-orange-100 text-amber-800 flex items-center justify-center shrink-0">
        <AlertTriangle className="w-5 h-5" />
      </div>

      {/* Safety Notice Content */}
      <div>
        <h3 className="text-sm font-bold text-amber-950 mb-1">
          {title}
        </h3>
        <p className="text-xs text-amber-900/80 leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
}
