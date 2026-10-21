import React from "react";
import { History, CheckCircle2, AlertTriangle, AlertOctagon } from "lucide-react";

interface SummaryCardItem {
  id: string;
  label: string;
  value: string;
  iconName: string;
  iconBg: string;
  iconColor: string;
}

interface LogSummaryCardsProps {
  cards: SummaryCardItem[];
}

export default function LogSummaryCards({ cards }: LogSummaryCardsProps) {
  const getIcon = (name: string) => {
    switch (name) {
      case "History":
        return <History className="w-5 h-5 text-white" />;
      case "CheckCircle2":
        return <CheckCircle2 className="w-5 h-5 text-emerald-700" />;
      case "AlertTriangle":
        return <AlertTriangle className="w-5 h-5 text-amber-800" />;
      case "AlertOctagon":
        return <AlertOctagon className="w-5 h-5 text-red-700" />;
      default:
        return <History className="w-5 h-5" />;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
      {cards.map((card) => (
        <div
          key={card.id}
          className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center justify-between"
        >
          <div>
            <span className="block text-[11px] font-semibold tracking-wider text-slate-400 uppercase mb-1">
              {card.label}
            </span>
            <span className="text-2xl md:text-3xl font-extrabold text-slate-800 tracking-tight">
              {card.value}
            </span>
          </div>

          <div
            className={`w-12 h-12 rounded-xl ${card.iconBg} flex items-center justify-center shrink-0 shadow-xs`}
          >
            {getIcon(card.iconName)}
          </div>
        </div>
      ))}
    </div>
  );
}
