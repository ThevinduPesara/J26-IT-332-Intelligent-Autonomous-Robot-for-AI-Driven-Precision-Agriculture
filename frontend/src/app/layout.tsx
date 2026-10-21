import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AgriBot IoT - Intelligent Autonomous Precision Agriculture",
  description: "Real-time Autonomous Robot Telemetry & Monitoring System",
  icons: {
    icon: "/agribot-logo.svg",
    shortcut: "/agribot-logo.svg",
    apple: "/agribot-logo.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-[#f8fafc] antialiased">
      <body className={`${inter.className} min-h-screen bg-[#f8fafc] text-slate-900`}>
        <div className="flex min-h-screen bg-[#f8fafc]">
          {/* Left Navigation Sidebar */}
          <Sidebar />

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#f8fafc]">
            {/* Top Navigation Header */}
            <Header />

            {/* Page View */}
            <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
