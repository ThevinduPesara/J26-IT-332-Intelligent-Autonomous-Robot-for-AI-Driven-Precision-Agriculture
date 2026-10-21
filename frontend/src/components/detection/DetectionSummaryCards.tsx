import React from "react";
import { Crosshair, Leaf, Bug, Zap } from "lucide-react";

interface SummaryItem {
  id: string;
  label: string;
  value: string;
  iconName: string;
  iconBg: string;
  iconColor: string;
}

interface DetectionSummaryCardsProps {
  cards: SummaryItem[];
}

export default function DetectionSummaryCards({
  cards,
}: DetectionSummaryCardsProps) {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "Crosshair":
        return <Crosshair className="w-5 h-5 text-emerald-700" />;
      case "Leaf":
        return <Leaf className="w-5 h-5 text-emerald-700" />;
      case "Bug":
        return <Bug className="w-5 h-5 text-red-700" />;
      case "Zap":
        return <Zap className="w-5 h-5 text-amber-700 fill-amber-700" />;
      default:
        return <Crosshair className="w-5 h-5 text-emerald-700" />;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
      {cards.map((item) => (
        <div
          key={item.id}
          className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center justify-between"
        >
          <div>
            <span className="block text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1">
              {item.label}
            </span>
            <span
              className={`text-2xl md:text-3xl font-extrabold tracking-tight ${
                item.id === "pests" ? "text-red-600" : "text-slate-800"
              }`}
            >
              {item.value}
            </span>
          </div>

          <div
            className={`w-12 h-12 rounded-xl ${item.iconBg} flex items-center justify-center shrink-0 shadow-xs`}
          >
            {getIcon(item.iconName)}
          </div>
        </div>
      ))}
    </div>
  );
}
