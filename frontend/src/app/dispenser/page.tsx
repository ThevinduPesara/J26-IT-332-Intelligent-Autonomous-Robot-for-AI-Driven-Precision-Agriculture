import React from "react";
import DispenserHeader from "@/components/dispenser/DispenserHeader";
import MainDispenserCard from "@/components/dispenser/MainDispenserCard";
import RelayStatusCard from "@/components/dispenser/RelayStatusCard";
import HopperCard from "@/components/dispenser/HopperCard";
import SafetyNoticeCard from "@/components/dispenser/SafetyNoticeCard";
import { dispenserData } from "@/data/dispenserData";

export const metadata = {
  title: "Seed Dispenser Control - AgriBot IoT",
};

/**
 * SEED DISPENSER CONTROL PAGE (/dispenser)
 * Fully modular and accessible for all development levels.
 */
export default function SeedDispenserPage() {
  return (
    <div className="space-y-6">
      {/* 1. Header Section */}
      <DispenserHeader
        title={dispenserData.header.title}
        description={dispenserData.header.description}
        protocol={dispenserData.header.protocol}
      />

      {/* 2. Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Column (2 Cols): Main Dispenser Card & Safety Notice */}
        <div className="lg:col-span-2 space-y-6">
          <MainDispenserCard
            title={dispenserData.primaryDispenser.title}
            unitId={dispenserData.primaryDispenser.unitId}
            hopperCap={dispenserData.primaryDispenser.hopperCap}
            statusBadge={dispenserData.primaryDispenser.statusBadge}
            metrics={dispenserData.primaryDispenser.metrics}
            actuationTitle={dispenserData.primaryDispenser.actuationBox.title}
            actuationDescription={
              dispenserData.primaryDispenser.actuationBox.description
            }
            initialState={
              dispenserData.primaryDispenser.actuationBox.initialState
            }
          />

          <SafetyNoticeCard
            title={dispenserData.safetyNotice.title}
            description={dispenserData.safetyNotice.description}
          />
        </div>

        {/* Right Column (1 Col): IoT Relay Status & Hopper Diagnostics */}
        <div className="space-y-6">
          <RelayStatusCard
            title={dispenserData.relayStatus.title}
            connectionText={dispenserData.relayStatus.connectionText}
            statusBadge={dispenserData.relayStatus.statusBadge}
            signalStrengthRssi={dispenserData.relayStatus.signalStrengthRssi}
            signalPercentage={dispenserData.relayStatus.signalPercentage}
            packetLatency={dispenserData.relayStatus.packetLatency}
            relayFirmware={dispenserData.relayStatus.relayFirmware}
          />

          <HopperCard
            title={dispenserData.hopperDiagnostics.title}
            percentage={dispenserData.hopperDiagnostics.percentage}
            statusText={dispenserData.hopperDiagnostics.statusText}
            coverageText={dispenserData.hopperDiagnostics.coverageText}
            autoCalibrationStatus={
              dispenserData.hopperDiagnostics.autoCalibrationStatus
            }
          />
        </div>
      </div>
    </div>
  );
}
