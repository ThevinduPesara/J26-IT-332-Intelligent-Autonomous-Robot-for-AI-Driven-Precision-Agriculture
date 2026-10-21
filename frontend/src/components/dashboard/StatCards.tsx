import React from "react";
import { Bot, Navigation, Video, Crosshair } from "lucide-react";

interface StatItem {
  id: string;
  label: string;
  value: string;
  subtext: string;
  badge?: string;
  statusColor?: string;
  iconName: string;
}

interface StatCardsProps {
  stats: StatItem[];
}

export default function StatCards({ stats }: StatCardsProps) {
  // Helper function to pick icon based on name
  const getIcon = (name: string) => {
    switch (name) {
      case "Bot":
        return <Bot className="w-5 h-5 text-emerald-700" />;
      case "Navigation":
        return <Navigation className="w-5 h-5 text-emerald-700" />;
      case "Video":
        return <Video className="w-5 h-5 text-emerald-700" />;
      case "Crosshair":
        return <Crosshair className="w-5 h-5 text-emerald-700" />;
      default:
        return <Bot className="w-5 h-5 text-emerald-700" />;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.id}
          className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between"
        >
          {/* Label and Icon */}
          <div className="flex items-center justify-between mb-4">
            <span className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
              {stat.label}
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center">
              {getIcon(stat.iconName)}
            </div>
          </div>

          {/* Value and details */}
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              {/* Optional live dot if status is active */}
              {stat.statusColor && (
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
              )}
              <span className="text-xl font-bold text-slate-800">
                {stat.value}
              </span>
              {stat.badge && (
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100">
                  {stat.badge}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 font-medium">{stat.subtext}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
