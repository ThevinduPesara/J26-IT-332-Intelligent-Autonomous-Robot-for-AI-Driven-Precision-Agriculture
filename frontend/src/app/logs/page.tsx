"use client";

import React, { useState } from "react";
import LogSummaryCards from "@/components/logs/LogSummaryCards";
import LogFilterBar from "@/components/logs/LogFilterBar";
import LogTable from "@/components/logs/LogTable";
import LogPagination from "@/components/logs/LogPagination";
import { logsData } from "@/data/logsData";

/**
 * ACTIVITY LOGS PAGE (/logs)
 * Fully modular, clean, and beginner-friendly structure.
 */
export default function ActivityLogsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEventType, setSelectedEventType] = useState("all");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Filter logs based on search term and selected filters
  const filteredLogs = logsData.eventLogs.filter((log) => {
    const matchesSearch =
      log.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.subtitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.plantDetections.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType =
      selectedEventType === "all" || log.type === selectedEventType;

    return matchesSearch && matchesType;
  });

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      alert("Activity logs synchronized with live telemetry stream!");
    }, 1000);
  };

  return (
    <div className="space-y-6">
      {/* 1. Top Row: 4 Metric Summary Cards */}
      <section>
        <LogSummaryCards cards={logsData.summaryCards} />
      </section>

      {/* 2. Filter Bar: Search, Type dropdown, Status dropdown, Export & Refresh */}
      <section>
        <LogFilterBar
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          selectedEventType={selectedEventType}
          onEventTypeChange={setSelectedEventType}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />
      </section>

      {/* 3. Event Logs Table */}
      <section>
        <LogTable logs={filteredLogs} />
      </section>

      {/* 4. Pagination Footer */}
      <section>
        <LogPagination
          showingText={logsData.pagination.showingText}
          totalPages={logsData.pagination.totalPages}
        />
      </section>
    </div>
  );
}
