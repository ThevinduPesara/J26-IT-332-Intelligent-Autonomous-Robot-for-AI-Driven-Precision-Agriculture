import React from "react";
import { FlaskConical, AlertTriangle, TrendingUp } from "lucide-react";

interface InsightItem {
  id: string;
  badgeLabel: string;
  badgeType: string;
  metaText: string;
  title: string;
  description: string;
  progress: number;
  progressBarColor: string;
}

interface AgronomyInsightsProps {
  insights: InsightItem[];
}

export default function AgronomyInsights({ insights }: AgronomyInsightsProps) {
  const getBadgeStyle = (type: string) => {
    switch (type) {
      case "teal":
        return "bg-teal-50 text-teal-800 border-teal-200";
      case "red":
        return "bg-red-50 text-red-800 border-red-200";
      case "green":
        return "bg-emerald-50 text-emerald-800 border-emerald-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const getBadgeIcon = (id: string) => {
    switch (id) {
      case "nutrient":
        return <FlaskConical className="w-3.5 h-3.5 text-teal-700 mr-1" />;
      case "pest":
        return <AlertTriangle className="w-3.5 h-3.5 text-red-600 mr-1" />;
      case "growth":
        return <TrendingUp className="w-3.5 h-3.5 text-emerald-700 mr-1" />;
      default:
        return null;
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      {insights.map((item) => (
        <div
          key={item.id}
          className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between"
        >
          <div>
            {/* Top row: Badge and Meta Text */}
            <div className="flex items-center justify-between gap-2 mb-3">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getBadgeStyle(
                  item.badgeType
                )}`}
              >
                {getBadgeIcon(item.id)}
                {item.badgeLabel}
              </span>
              <span className="text-[11px] font-medium text-slate-400">
                {item.metaText}
              </span>
            </div>

            {/* Title */}
            <h3 className="text-base font-bold text-slate-800 mb-2 leading-snug">
              {item.title}
            </h3>

            {/* Description */}
            <p className="text-xs text-slate-500 leading-relaxed mb-6">
              {item.description}
            </p>
          </div>

          {/* Bottom Progress Bar */}
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${item.progressBarColor}`}
              style={{ width: `${item.progress}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
