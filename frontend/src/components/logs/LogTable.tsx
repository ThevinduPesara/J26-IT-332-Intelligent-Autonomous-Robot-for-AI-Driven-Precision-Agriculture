import React from "react";

export interface LogItem {
  id: number;
  timestamp: string;
  title: string;
  subtitle: string;
  movement: {
    status: string;
    type: string;
  };
  plantDetections: string;
  npk: string;
  seedDispenser: string;
  connection: string;
  type: string;
}

interface LogTableProps {
  logs: LogItem[];
}

export default function LogTable({ logs }: LogTableProps) {
  // Helper to style movement badges
  const getMovementBadgeClass = (type: string) => {
    switch (type) {
      case "moving":
        return "bg-emerald-100/80 text-emerald-800 border border-emerald-200";
      case "warning":
        return "bg-amber-100/80 text-amber-900 border border-amber-200";
      case "stationary":
        return "bg-slate-100 text-slate-700 border border-slate-200";
      default:
        return "bg-slate-100 text-slate-700";
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          {/* Table Header */}
          <thead>
            <tr className="border-b border-slate-200/80 bg-slate-50/50 text-[11px] font-semibold text-slate-400 tracking-wider uppercase">
              <th className="py-4 px-5">TIMESTAMP</th>
              <th className="py-4 px-5">EVENT DESCRIPTION</th>
              <th className="py-4 px-5">ROBOT MOVEMENT</th>
              <th className="py-4 px-5">PLANT DETECTIONS</th>
              <th className="py-4 px-5">NPK SENSOR READINGS</th>
              <th className="py-4 px-5">SEED DISPENSER</th>
              <th className="py-4 px-5">CONNECTION</th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {logs.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-slate-400">
                  No matching event logs found.
                </td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr
                  key={log.id}
                  className="hover:bg-slate-50/60 transition-colors"
                >
                  {/* Timestamp */}
                  <td className="py-4 px-5 font-mono text-[11px] text-slate-500 whitespace-pre-line">
                    {log.timestamp}
                  </td>

                  {/* Event Description */}
                  <td className="py-4 px-5 max-w-[200px]">
                    <span className="block font-bold text-slate-800 leading-snug">
                      {log.title}
                    </span>
                    <span className="block text-[11px] text-slate-400 mt-0.5 leading-snug">
                      {log.subtitle}
                    </span>
                  </td>

                  {/* Robot Movement */}
                  <td className="py-4 px-5 whitespace-nowrap">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-lg text-[11px] font-semibold text-center whitespace-pre-line ${getMovementBadgeClass(
                        log.movement.type
                      )}`}
                    >
                      {log.movement.status}
                    </span>
                  </td>

                  {/* Plant Detections */}
                  <td className="py-4 px-5 font-medium whitespace-pre-line text-slate-700">
                    {log.plantDetections}
                  </td>

                  {/* NPK Sensor Readings */}
                  <td className="py-4 px-5 font-mono text-[11px] text-slate-600 whitespace-pre-line leading-relaxed">
                    {log.npk}
                  </td>

                  {/* Seed Dispenser */}
                  <td className="py-4 px-5 font-medium text-slate-800 whitespace-nowrap">
                    {log.seedDispenser}
                  </td>

                  {/* Connection */}
                  <td className="py-4 px-5 whitespace-nowrap">
                    <div className="flex items-center gap-1.5 font-medium text-emerald-700">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                      <span>{log.connection}</span>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
