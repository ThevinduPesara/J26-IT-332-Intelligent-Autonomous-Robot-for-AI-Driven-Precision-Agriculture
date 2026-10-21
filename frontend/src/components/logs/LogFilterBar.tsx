"use client";

import React from "react";
import { Search, Download, RefreshCw } from "lucide-react";

interface LogFilterBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedEventType: string;
  onEventTypeChange: (value: string) => void;
  selectedStatus: string;
  onStatusChange: (value: string) => void;
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export default function LogFilterBar({
  searchTerm,
  onSearchChange,
  selectedEventType,
  onEventTypeChange,
  selectedStatus,
  onStatusChange,
  onRefresh,
  isRefreshing = false,
}: LogFilterBarProps) {
  const handleExportCsv = () => {
    alert("Exporting activity logs as CSV file...");
  };

  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3.5">
      {/* Left: Search & Filter Dropdowns */}
      <div className="flex flex-wrap items-center gap-3 flex-1">
        {/* Search Input Box */}
        <div className="relative min-w-[220px] sm:min-w-[260px] flex-1 sm:flex-initial">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search event logs..."
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200/90 rounded-xl text-xs md:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition"
          />
        </div>

        {/* Event Types Dropdown */}
        <select
          value={selectedEventType}
          onChange={(e) => onEventTypeChange(e.target.value)}
          aria-label="Filter by event type"
          className="bg-white border border-slate-200/90 rounded-xl px-3.5 py-2.5 text-xs md:text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-700/20 cursor-pointer"
        >
          <option value="all">All Event Types</option>
          <option value="navigation">Navigation</option>
          <option value="warning">Obstacle & Alerts</option>
          <option value="soil">Soil Sampling</option>
          <option value="dispenser">Dispenser</option>
        </select>

        {/* Statuses Filter Dropdown */}
        <select
          value={selectedStatus}
          onChange={(e) => onStatusChange(e.target.value)}
          aria-label="Filter by status"
          className="bg-white border border-slate-200/90 rounded-xl px-3.5 py-2.5 text-xs md:text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-700/20 cursor-pointer"
        >
          <option value="all">All Statuses</option>
          <option value="stable">Stable</option>
          <option value="warning">Warning</option>
          <option value="active">Active</option>
        </select>
      </div>

      {/* Right: Export CSV & Refresh Live Buttons */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Export CSV Button */}
        <button
          onClick={handleExportCsv}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs md:text-sm font-semibold text-slate-700 bg-white border border-slate-200/90 hover:bg-slate-50 transition active:scale-98 cursor-pointer shadow-2xs"
        >
          <Download className="w-4 h-4 text-slate-500" />
          Export CSV
        </button>

        {/* Refresh Live Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs md:text-sm font-semibold text-white bg-[#0f5132] hover:bg-emerald-900 transition active:scale-98 cursor-pointer shadow-xs disabled:opacity-75"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh Live
        </button>
      </div>
    </div>
  );
}
