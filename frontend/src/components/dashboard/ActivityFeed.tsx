import React from "react";
import { CheckCircle2, Crosshair, Zap } from "lucide-react";

interface ActivityItem {
  id: number;
  title: string;
  description: string;
  time: string;
  icon: string;
  iconColor: string;
  bgColor: string;
}

interface ActivityFeedProps {
  activities: ActivityItem[];
}

export default function ActivityFeed({ activities }: ActivityFeedProps) {
  // Helper to render icon dynamically
  const renderIcon = (iconName: string, iconColor: string) => {
    switch (iconName) {
      case "CheckCircle2":
        return <CheckCircle2 className={`w-5 h-5 ${iconColor}`} />;
      case "Crosshair":
        return <Crosshair className={`w-5 h-5 ${iconColor}`} />;
      case "Zap":
        return <Zap className={`w-5 h-5 ${iconColor}`} />;
      default:
        return <CheckCircle2 className={`w-5 h-5 ${iconColor}`} />;
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 md:p-7 border border-slate-200/80 shadow-xs">
      {/* Feed Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-slate-800">
          Recent System Activity Feed
        </h3>
        <span className="text-xs font-mono font-medium text-slate-400">
          Live Telemetry Stream
        </span>
      </div>

      {/* Activity List */}
      <div className="space-y-3">
        {activities.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50/70 hover:bg-slate-50 transition border border-slate-100"
          >
            <div className="flex items-center gap-3.5">
              <div
                className={`w-10 h-10 rounded-xl ${item.bgColor} flex items-center justify-center shrink-0`}
              >
                {renderIcon(item.icon, item.iconColor)}
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-800 leading-snug">
                  {item.title}
                </h4>
                <p className="text-xs text-slate-500 mt-0.5">{item.description}</p>
              </div>
            </div>

            {/* Time Stamp */}
            <span className="text-xs font-mono text-slate-400 shrink-0 ml-4">
              {item.time}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
