"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Navigation,
  Video,
  Crosshair,
  FlaskConical,
  Tractor,
  History,
  LineChart,
  Menu,
  X,
} from "lucide-react";

export const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Robot Navigation", href: "/navigation", icon: Navigation },
  { name: "Live Camera", href: "/camera", icon: Video },
  { name: "AI Plant Detection", href: "/detection", icon: Crosshair },
  { name: "Soil NPK Monitoring", href: "/soil", icon: FlaskConical },
  { name: "Seed Dispenser Control", href: "/dispenser", icon: Tractor },
  { name: "Activity Logs", href: "/logs", icon: History },
  { name: "Analysis", href: "/analysis", icon: LineChart },
];

export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Toggle Button */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-slate-200 text-slate-700 hover:bg-slate-50 transition"
        aria-label="Toggle navigation"
      >
        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Backdrop for Mobile */}
      {mobileOpen && (
        <div
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs z-40 md:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:sticky top-0 left-0 h-screen w-64 bg-[#f8fafc] border-r border-slate-200/80 flex flex-col justify-between py-6 px-4 z-40 transition-transform duration-300 ease-in-out ${
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div>
          {/* Logo Section */}
          <Link href="/" className="flex items-center gap-3 px-3 mb-8 group">
            {/* Custom AgriBot Plant Logo */}
            <div className="w-9 h-9 relative shrink-0 shadow-sm shadow-emerald-900/20 transition-transform group-hover:scale-105">
              <Image
                src="/agribot-logo.svg"
                alt="AgriBot Logo"
                width={36}
                height={36}
                className="w-full h-full object-contain"
                priority
              />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-slate-900 text-lg leading-tight tracking-tight">
                AgriBot <span className="text-emerald-700">IoT</span>
              </span>
              <span className="text-[11px] font-medium text-slate-400">
                Precision Ag Tech
              </span>
            </div>
          </Link>

          {/* Navigation Items List */}
          <nav className="space-y-1.5">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname?.startsWith(item.href);

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? "bg-[#18533a] text-white shadow-sm shadow-emerald-950/15"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/60"
                  }`}
                >
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-white" : "text-slate-500"
                    }`}
                  />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer info inside sidebar */}
        <div className="px-3 pt-4 border-t border-slate-200/60 text-xs text-slate-400">
          <p>AgriBot System v2.4</p>
          <p className="text-[10px] text-slate-400/80">Autonomous Unit Node</p>
        </div>
      </aside>
    </>
  );
}
