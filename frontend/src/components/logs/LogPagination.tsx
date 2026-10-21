"use client";

import React, { useState } from "react";

interface LogPaginationProps {
  showingText: string;
  totalPages: number;
}

export default function LogPagination({
  showingText,
  totalPages,
}: LogPaginationProps) {
  const [currentPage, setCurrentPage] = useState(1);

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs font-medium text-slate-500 pt-2">
      {/* Left: Showing info */}
      <span>{showingText}</span>

      {/* Right: Page numbers and Prev/Next */}
      <div className="flex items-center gap-1.5 self-center sm:self-auto">
        <button
          onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
          disabled={currentPage === 1}
          className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 transition disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
        >
          Previous
        </button>

        {/* Page Buttons */}
        <button
          onClick={() => setCurrentPage(1)}
          className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold transition cursor-pointer ${
            currentPage === 1
              ? "bg-[#0f5132] text-white shadow-xs"
              : "border border-slate-200 bg-white hover:bg-slate-50 text-slate-700"
          }`}
        >
          1
        </button>

        <button
          onClick={() => setCurrentPage(2)}
          className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold transition cursor-pointer ${
            currentPage === 2
              ? "bg-[#0f5132] text-white shadow-xs"
              : "border border-slate-200 bg-white hover:bg-slate-50 text-slate-700"
          }`}
        >
          2
        </button>

        <button
          onClick={() => setCurrentPage(3)}
          className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold transition cursor-pointer ${
            currentPage === 3
              ? "bg-[#0f5132] text-white shadow-xs"
              : "border border-slate-200 bg-white hover:bg-slate-50 text-slate-700"
          }`}
        >
          3
        </button>

        <span className="px-1 text-slate-400">...</span>

        <button
          onClick={() => setCurrentPage(totalPages)}
          className={`px-2.5 h-8 rounded-lg flex items-center justify-center font-semibold transition cursor-pointer ${
            currentPage === totalPages
              ? "bg-[#0f5132] text-white shadow-xs"
              : "border border-slate-200 bg-white hover:bg-slate-50 text-slate-700"
          }`}
        >
          {totalPages}
        </button>

        <button
          onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 transition disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  );
}
