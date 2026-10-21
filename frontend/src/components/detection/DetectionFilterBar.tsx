"use client";

import React from "react";
import { Search, RefreshCw } from "lucide-react";

interface DetectionFilterBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  sortBy: string;
  onSortByChange: (sort: string) => void;
  onRunScan: () => void;
  isScanning?: boolean;
}

export default function DetectionFilterBar({
  searchTerm,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  sortBy,
  onSortByChange,
  onRunScan,
  isScanning = false,
}: DetectionFilterBarProps) {
  const filterOptions = ["All Records", "Healthy", "Moderate", "Poor"];

  return (
    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      {/* Left: Search input and Status Pills */}
      <div className="flex flex-wrap items-center gap-3 flex-1">
        {/* Search by Plant ID Input */}
        <div className="relative min-w-[220px] sm:min-w-[260px] flex-1 sm:flex-initial">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by Plant ID (#PLT-...)"
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200/90 rounded-xl text-xs md:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-700/20 focus:border-emerald-700 transition"
          />
        </div>

        {/* Status Pill Buttons */}
        <div className="flex items-center gap-1.5 p-1 bg-white border border-slate-200/80 rounded-xl">
          {filterOptions.map((opt) => {
            const isSelected = statusFilter === opt;
            return (
              <button
                key={opt}
                onClick={() => onStatusFilterChange(opt)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                  isSelected
                    ? "bg-[#18533a] text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                {opt}
              </button>
            );
          })}
        </div>
      </div>

      {/* Right: Sort By Dropdown and Run Scan Button */}
      <div className="flex items-center gap-3 shrink-0">
        <select
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value)}
          aria-label="Sort plant records"
          className="bg-white border border-slate-200/90 rounded-xl px-3.5 py-2.5 text-xs md:text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-emerald-700/20 cursor-pointer"
        >
          <option value="confidence-desc">Sort by: Confidence (High to Low)</option>
          <option value="confidence-asc">Sort by: Confidence (Low to High)</option>
          <option value="recent">Sort by: Most Recent</option>
        </select>

        <button
          onClick={onRunScan}
          disabled={isScanning}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs md:text-sm font-semibold text-white bg-[#0f5132] hover:bg-emerald-900 transition active:scale-98 cursor-pointer shadow-xs disabled:opacity-75"
        >
          <RefreshCw className={`w-4 h-4 ${isScanning ? "animate-spin" : ""}`} />
          {isScanning ? "Scanning..." : "Run Scan"}
        </button>
      </div>
    </div>
  );
}
