import React from "react";
import NpkHeader from "@/components/soil/NpkHeader";
import MacronutrientCard from "@/components/soil/MacronutrientCard";
import NutrientTrendChart from "@/components/soil/NutrientTrendChart";
import SensorVsVisionCard from "@/components/soil/SensorVsVisionCard";
import { soilData } from "@/data/soilData";

export const metadata = {
  title: "Soil NPK Monitoring - AgriBot IoT",
};

/**
 * SOIL NPK MONITORING PAGE (/soil)
 * Fully modular and accessible for all development levels.
 */
export default function SoilNpkPage() {
  return (
    <div className="space-y-6">
      {/* 1. Header Section */}
      <NpkHeader
        title={soilData.header.title}
        sensorBadge={soilData.header.sensorBadge}
        description={soilData.header.description}
      />

      {/* 2. Top Row: Macronutrient N, P, K Metric Cards (3 Columns) */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {soilData.macronutrients.map((item) => (
          <MacronutrientCard
            key={item.id}
            category={item.category}
            name={item.name}
            symbol={item.symbol}
            value={item.value}
            unit={item.unit}
            rangeText={item.rangeText}
            percentage={item.percentage}
            status={item.status}
            statusType={item.statusType as "optimal" | "moderate"}
            updatedTime={item.updatedTime}
            targetRange={item.targetRange}
            barColor={item.barColor}
          />
        ))}
      </section>

      {/* 3. Bottom Row: 24-Hour Nutrient Trend (2 Cols) & Sensor vs AI Vision (1 Col) */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
        <div className="lg:col-span-2">
          <NutrientTrendChart
            title={soilData.trendChart.title}
            subtitle={soilData.trendChart.subtitle}
            legend={soilData.trendChart.legend}
            timeLabels={soilData.trendChart.timeLabels}
          />
        </div>

        <div className="lg:col-span-1">
          <SensorVsVisionCard
            title={soilData.sensorVsVision.title}
            paragraph1={soilData.sensorVsVision.paragraph1}
            paragraph2={soilData.sensorVsVision.paragraph2}
            calibratedBadge={soilData.sensorVsVision.calibratedBadge}
          />
        </div>
      </section>
    </div>
  );
}
