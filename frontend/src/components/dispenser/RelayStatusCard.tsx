"use client";

import React, { useState } from "react";
import { Settings, Check, Wifi, WifiOff } from "lucide-react";

interface RelayStatusCardProps {
  title: string;
  connectionText: string;
  statusBadge: string;
  signalStrengthRssi: string;
  signalPercentage: number;
  packetLatency: string;
  relayFirmware: string;
  ipAddress?: string;
  isConnected?: boolean;
  onIpChange?: (newIp: string) => void;
}

export default function RelayStatusCard({
  title,
  connectionText,
  statusBadge,
  signalStrengthRssi,
  signalPercentage,
  packetLatency,
  relayFirmware,
  ipAddress = "http://192.168.8.108",
  isConnected = false,
  onIpChange,
}: RelayStatusCardProps) {
  const [isEditingIp, setIsEditingIp] = useState(false);
  const [tempIp, setTempIp] = useState(ipAddress);

  const handleSaveIp = () => {
    if (onIpChange && tempIp.trim()) {
      onIpChange(tempIp.trim());
    }
    setIsEditingIp(false);
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col justify-between">
      <div>
        {/* Card Title & IP Setting */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-slate-800">{title}</h3>
          <button
            onClick={() => setIsEditingIp((prev) => !prev)}
            title="Configure ESP32 IP"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* IP Config Box (When toggled) */}
        {isEditingIp && (
          <div className="mb-4 p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <label className="text-[11px] font-semibold text-slate-600 block">
              ESP32 IP / Host URL:
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={tempIp}
                onChange={(e) => setTempIp(e.target.value)}
                placeholder="http://192.168.8.108"
                className="flex-1 px-2.5 py-1 text-xs bg-white border border-slate-200 rounded-lg text-slate-800 font-mono focus:outline-hidden focus:border-emerald-600"
              />
              <button
                onClick={handleSaveIp}
                className="px-2.5 py-1 bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 hover:bg-emerald-800"
              >
                <Check className="w-3 h-3" /> Save
              </button>
            </div>
          </div>
        )}

        {/* Connection Status Box */}
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-100 mb-5">
          <div className="flex items-center gap-2.5">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isConnected ? "bg-emerald-600" : "bg-rose-500 animate-pulse"
              }`}
            />
            <span className="text-xs md:text-sm font-semibold text-slate-800">
              {connectionText}
            </span>
          </div>
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded-md border ${
              isConnected
                ? "text-emerald-700 bg-emerald-50 border-emerald-100"
                : "text-amber-700 bg-amber-50 border-amber-200"
            }`}
          >
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
              className={`h-full rounded-full transition-all duration-500 ${
                isConnected ? "bg-emerald-700" : "bg-slate-300"
              }`}
              style={{ width: `${isConnected ? signalPercentage : 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Packet Latency & Relay Firmware Info */}
      <div className="space-y-2 text-xs pt-3 border-t border-slate-100">
        <div className="flex justify-between items-center">
          <span className="text-slate-400 font-medium">Device Endpoint</span>
          <span className="font-mono font-semibold text-slate-700 text-[11px] truncate max-w-[170px]" title={ipAddress}>
            {ipAddress}
          </span>
        </div>
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
