import React from "react";
import { Video, Crosshair, HardDrive } from "lucide-react";

interface CameraMetricItem {
  id: string;
  title: string;
  value: string;
  iconName: string;
}

interface CameraMetricsRowProps {
  metrics: CameraMetricItem[];
}

export default function CameraMetricsRow({ metrics }: CameraMetricsRowProps) {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "Video":
        return <Video className="w-5 h-5 text-emerald-700" />;
      case "Crosshair":
        return <Crosshair className="w-5 h-5 text-emerald-700" />;
      case "HardDrive":
        return <HardDrive className="w-5 h-5 text-amber-700" />;
      default:
        return <Video className="w-5 h-5 text-emerald-700" />;
    }
  };

  const getBg = (iconName: string) => {
    switch (iconName) {
      case "Video":
        return "bg-emerald-50";
      case "Crosshair":
        return "bg-teal-50";
      case "HardDrive":
        return "bg-amber-50";
      default:
        return "bg-slate-50";
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      {metrics.map((item) => (
        <div
          key={item.id}
          className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center gap-4"
        >
          {/* Icon Box */}
          <div
            className={`w-12 h-12 rounded-xl ${getBg(
              item.iconName
            )} flex items-center justify-center shrink-0`}
          >
            {getIcon(item.iconName)}
          </div>

          {/* Details */}
          <div>
            <span className="block text-xs font-medium text-slate-400 mb-0.5">
              {item.title}
            </span>
            <span className="text-lg font-bold text-slate-800">
              {item.value}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
