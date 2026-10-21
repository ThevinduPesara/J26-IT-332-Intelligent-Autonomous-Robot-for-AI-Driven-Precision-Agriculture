"use client";

import React, { useState } from "react";
import DetectionSummaryCards from "@/components/detection/DetectionSummaryCards";
import AgronomyInsights from "@/components/detection/AgronomyInsights";
import DetectionFilterBar from "@/components/detection/DetectionFilterBar";
import PlantCardGrid from "@/components/detection/PlantCardGrid";
import { detectionData } from "@/data/detectionData";

/**
 * AI PLANT DETECTION PAGE (/detection)
 * Fully modular and simple to maintain for all experience levels.
 */
export default function AiPlantDetectionPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All Records");
  const [sortBy, setSortBy] = useState("confidence-desc");
  const [isScanning, setIsScanning] = useState(false);

  // Filter plants based on search term & status button
  const filteredPlants = detectionData.plantCards.filter((plant) => {
    const matchesSearch =
      plant.id.toLowerCase().includes(searchTerm.toLowerCase().replace("#", "")) ||
      plant.species.toLowerCase().includes(searchTerm.toLowerCase()) ||
      plant.zone.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "All Records" || plant.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  // Sort plants
  const sortedPlants = [...filteredPlants].sort((a, b) => {
    if (sortBy === "confidence-desc") {
      return parseInt(b.confidence) - parseInt(a.confidence);
    }
    if (sortBy === "confidence-asc") {
      return parseInt(a.confidence) - parseInt(b.confidence);
    }
    return 0;
  });

  const handleRunScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      alert("AI Inference Scan complete! 6 plants analyzed.");
    }, 1200);
  };

  return (
    <div className="space-y-6">
      {/* 1. Top Row: 4 Metric Cards */}
      <section>
        <DetectionSummaryCards cards={detectionData.summaryCards} />
      </section>

      {/* 2. Middle Row: 3 Agronomy Diagnostic Cards */}
      <section>
        <AgronomyInsights insights={detectionData.insights} />
      </section>

      {/* 3. Filter Bar: Search, Status Pills, Sort, and Run Scan */}
      <section>
        <DetectionFilterBar
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          sortBy={sortBy}
          onSortByChange={setSortBy}
          onRunScan={handleRunScan}
          isScanning={isScanning}
        />
      </section>

      {/* 4. Plant Detection Grid Cards */}
      <section>
        <PlantCardGrid plants={sortedPlants} />
      </section>
    </div>
  );
}
