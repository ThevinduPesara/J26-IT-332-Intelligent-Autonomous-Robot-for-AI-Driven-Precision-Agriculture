import React from "react";

export default function Header() {
  return (
    <header className="w-full flex items-center justify-between py-4 px-6 md:px-8 bg-transparent">
      {/* Left: System Status Badge */}
      <div className="flex items-center gap-2">
        <div className="inline-flex items-center gap-2 bg-[#dcfce7] border border-emerald-200 text-emerald-850 text-xs font-semibold px-3 py-1.5 rounded-full shadow-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
          </span>
          System Online
        </div>
      </div>
    </header>
  );
}
