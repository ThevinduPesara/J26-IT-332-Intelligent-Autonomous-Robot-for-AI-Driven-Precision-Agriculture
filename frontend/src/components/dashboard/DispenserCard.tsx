"use client";

import React, { useState } from "react";

interface DispenserCardProps {
  initialStatus?: "ON" | "OFF";
}

export default function DispenserCard({
  initialStatus = "OFF",
}: DispenserCardProps) {
  const [status, setStatus] = useState<"ON" | "OFF">(initialStatus);

  const toggleStatus = () => {
    setStatus((prev) => (prev === "ON" ? "OFF" : "ON"));
  };

  const isOn = status === "ON";

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex items-center justify-between">
      {/* Label and Status */}
      <div>
        <span className="block text-[11px] font-semibold tracking-wider text-slate-400 uppercase leading-snug">
          SEED<br />DISPENSER<br />UNIT
        </span>
        <span
          className={`block text-xl font-bold mt-2 ${
            isOn ? "text-emerald-700" : "text-slate-800"
          }`}
        >
          {status}
        </span>
      </div>

      {/* Big Toggle Action Button */}
      <button
        onClick={toggleStatus}
        className={`px-6 py-4 rounded-xl text-sm font-semibold transition-all active:scale-95 cursor-pointer text-center ${
          isOn
            ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-700"
            : "bg-indigo-50 text-slate-700 hover:bg-indigo-100"
        }`}
      >
        Toggle
        <br />
        Dispenser
      </button>
    </div>
  );
}
