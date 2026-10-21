import React from "react";

interface RelayStatusCardProps {
  title: string;
  connectionText: string;
  statusBadge: string;
  signalStrengthRssi: string;
  signalPercentage: number;
  packetLatency: string;
  relayFirmware: string;
}

export default function RelayStatusCard({
  title,
  connectionText,
  statusBadge,
  signalStrengthRssi,
  signalPercentage,
  packetLatency,
  relayFirmware,
}: RelayStatusCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        {/* Card Title */}
        <h3 className="text-sm font-bold text-slate-800 mb-4">{title}</h3>

        {/* Connection Status Box */}
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-100 mb-5">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
            <span className="text-xs md:text-sm font-semibold text-slate-800">
              {connectionText}
            </span>
          </div>
          <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
            {statusBadge}
          </span>
        </div>

        {/* Signal Strength (RSSI) Progress Bar */}
        <div className="mb-5">
          <div className="flex justify-between items-center text-xs mb-1.5">
            <span className="font-medium text-slate-400">Signal Strength (RSSI)</span>
            <span className="font-mono font-bold text-slate-800">
              {signalStrengthRssi}
            </span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="bg-emerald-700 h-full rounded-full transition-all duration-500"
              style={{ width: `${signalPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Packet Latency & Relay Firmware Info */}
      <div className="space-y-2 text-xs pt-3 border-t border-slate-100">
        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Packet Latency</span>
          <span className="font-mono font-bold text-slate-800">{packetLatency}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Relay Firmware</span>
          <span className="font-mono font-semibold text-slate-600">{relayFirmware}</span>
        </div>
      </div>
    </div>
  );
}
