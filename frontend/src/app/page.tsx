import React from "react";
import HeroBanner from "@/components/dashboard/HeroBanner";
import PowerCard from "@/components/dashboard/PowerCard";
import StatCards from "@/components/dashboard/StatCards";
import CableTrack from "@/components/dashboard/CableTrack";
import SoilNutrient from "@/components/dashboard/SoilNutrient";
import DispenserCard from "@/components/dashboard/DispenserCard";
import ActivityFeed from "@/components/dashboard/ActivityFeed";
import { dashboardData } from "@/data/dashboardData";

/**
 * HOME / DASHBOARD PAGE
 * This page assembles all dashboard components together cleanly.
 * Any beginner or low-level developer can easily understand and maintain this file!
 */
export default function HomePage() {
  return (
    <div className="space-y-6">
      {/* 1. TOP ROW: Hero Status Banner & Power / Energy Card */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <HeroBanner
            unitName={dashboardData.robotInfo.unitName}
            statusBadge={dashboardData.robotInfo.statusBadge}
            description={dashboardData.robotInfo.description}
          />
        </div>
        <div>
          <PowerCard
            percentage={dashboardData.power.percentage}
            solarChargeRate={dashboardData.power.solarChargeRate}
            voltage={dashboardData.power.voltage}
            estimatedRuntime={dashboardData.power.estimatedRuntime}
          />
        </div>
      </section>

      {/* 2. SECOND ROW: 4 Core Telemetry Metric Cards */}
      <section>
        <StatCards stats={dashboardData.stats} />
      </section>

      {/* 3. THIRD ROW: Cable Track Overview, Soil Nutrient Sensors, and Seed Dispenser */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Plantation Cable Track Progress & Telemetry */}
        <div className="lg:col-span-2">
          <CableTrack
            title={dashboardData.cableTrack.title}
            spanText={dashboardData.cableTrack.spanText}
            statusText={dashboardData.cableTrack.statusText}
            currentPosition={dashboardData.cableTrack.currentPosition}
            totalLength={dashboardData.cableTrack.totalLength}
            winchSpeed={dashboardData.cableTrack.winchSpeed}
            tensionLoad={dashboardData.cableTrack.tensionLoad}
            motorTemp={dashboardData.cableTrack.motorTemp}
          />
        </div>

        {/* Right 1 Col: Soil Nutrients & Dispenser Control */}
        <div className="flex flex-col gap-6">
          <SoilNutrient
            statusBadge={dashboardData.soilNutrients.statusBadge}
            nutrients={dashboardData.soilNutrients.nutrients}
          />
          <DispenserCard />
        </div>
      </section>

      {/* 4. FOURTH ROW: Recent System Activity Feed */}
      <section>
        <ActivityFeed activities={dashboardData.recentActivity} />
      </section>
    </div>
  );
}
