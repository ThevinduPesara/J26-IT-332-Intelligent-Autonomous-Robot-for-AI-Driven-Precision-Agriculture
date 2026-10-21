"use client";

import React, { useState, useEffect, useCallback } from "react";
import DispenserHeader from "@/components/dispenser/DispenserHeader";
import MainDispenserCard from "@/components/dispenser/MainDispenserCard";
import RelayStatusCard from "@/components/dispenser/RelayStatusCard";
import HopperCard from "@/components/dispenser/HopperCard";
import SafetyNoticeCard from "@/components/dispenser/SafetyNoticeCard";
import { dispenserData } from "@/data/dispenserData";
import seedDispenserService, {
  DispenserConnectionState,
  DispenserStatusResponse,
} from "@/services/seedDispenserService";

export default function SeedDispenserClientView() {
  const [connectionState, setConnectionState] =
    useState<DispenserConnectionState>("disconnected");
  const [dispenserStatus, setDispenserStatus] =
    useState<DispenserStatusResponse | null>(null);
  const [isActive, setIsActive] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [baseUrl, setBaseUrl] = useState<string>("http://192.168.8.139");
  const [lastLatency, setLastLatency] = useState<string>("24 ms");
  const [feedbackMsg, setFeedbackMsg] = useState<{
    type: "success" | "error" | "info";
    text: string;
  } | null>(null);

  // Initialize service & polling
  useEffect(() => {
    const initialUrl = seedDispenserService.getBaseUrl();
    setBaseUrl(initialUrl);

    seedDispenserService.setCallbacks({
      onConnectionChange: (state, msg) => {
        setConnectionState(state);
        if (state === "disconnected") {
          setFeedbackMsg({
            type: "error",
            text: msg || "ESP32 Dispenser is unreachable on local network.",
          });
        } else if (state === "connected") {
          setFeedbackMsg(null);
        }
      },
      onStatusUpdate: (status) => {
        setDispenserStatus(status);
        setIsActive(status.dispenserActive);
      },
    });

    seedDispenserService.start();

    return () => {
      seedDispenserService.stop();
    };
  }, []);

  const handleIpChange = useCallback((newIp: string) => {
    setBaseUrl(newIp);
    seedDispenserService.setBaseUrl(newIp);
  }, []);

  // Handle Turn ON / OFF button click
  const handleToggle = async () => {
    setIsLoading(true);
    setFeedbackMsg(null);

    const startTime = performance.now();
    const nextState = !isActive;
    const ok = nextState
      ? await seedDispenserService.turnOn()
      : await seedDispenserService.turnOff();

    const elapsed = Math.round(performance.now() - startTime);
    setLastLatency(`${elapsed} ms`);

    setIsLoading(false);

    if (ok) {
      setIsActive(nextState);
      setFeedbackMsg({
        type: "success",
        text: nextState
          ? "Dispenser turned ON successfully. DC motors, Servo & N20 cycle active."
          : "Dispenser turned OFF successfully. All actuators parked.",
      });
    } else {
      setFeedbackMsg({
        type: "error",
        text: `Failed to communicate with Dispenser at ${baseUrl}. Please check Wi-Fi connection.`,
      });
    }
  };

  // Convert RSSI to signal percentage (e.g., -50dBm = 100%, -90dBm = 20%)
  const rssi = dispenserStatus?.wifiRSSI ?? -68;
  const signalPercentage = Math.max(
    10,
    Math.min(100, Math.round(2 * (rssi + 100)))
  );

  const isConnected = connectionState === "connected";

  return (
    <div className="space-y-6">
      {/* 1. Header Section */}
      <DispenserHeader
        title={dispenserData.header.title}
        description={dispenserData.header.description}
        protocol={{
          label: "Protocol / IP",
          value: `ESP32 REST (${baseUrl.replace(/^https?:\/\//, "")})`,
        }}
      />

      {/* Feedback Toast Banner */}
      {feedbackMsg && (
        <div
          className={`p-3.5 rounded-xl border text-xs font-semibold flex items-center justify-between transition-all ${
            feedbackMsg.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : feedbackMsg.type === "error"
              ? "bg-rose-50 border-rose-200 text-rose-800"
              : "bg-blue-50 border-blue-200 text-blue-800"
          }`}
        >
          <span>{feedbackMsg.text}</span>
          <button
            onClick={() => setFeedbackMsg(null)}
            className="text-[11px] underline opacity-75 hover:opacity-100 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 2. Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Column (2 Cols): Main Dispenser Card & Safety Notice */}
        <div className="lg:col-span-2 space-y-6">
          <MainDispenserCard
            title={dispenserData.primaryDispenser.title}
            unitId={dispenserData.primaryDispenser.unitId}
            hopperCap={dispenserData.primaryDispenser.hopperCap}
            statusBadge={
              isConnected
                ? isActive
                  ? "Active Dispensing"
                  : "Standby"
                : "Disconnected"
            }
            metrics={dispenserData.primaryDispenser.metrics}
            actuationTitle={dispenserData.primaryDispenser.actuationBox.title}
            actuationDescription={
              dispenserData.primaryDispenser.actuationBox.description
            }
            initialState={isActive}
            isActive={isActive}
            isLoading={isLoading}
            onToggle={handleToggle}
            esp32Online={isConnected}
          />

          <SafetyNoticeCard
            title={dispenserData.safetyNotice.title}
            description={dispenserData.safetyNotice.description}
          />
        </div>

        {/* Right Column (1 Col): IoT Relay Status & Hopper Diagnostics */}
        <div className="space-y-6">
          <RelayStatusCard
            title="IoT Relay / ESP32 Status"
            connectionText={
              isConnected ? "ESP32 Linked (REST API)" : "ESP32 Offline"
            }
            statusBadge={isConnected ? "Online" : "Offline"}
            signalStrengthRssi={`${rssi} dBm`}
            signalPercentage={signalPercentage}
            packetLatency={lastLatency}
            relayFirmware="ESP32-Dispenser-v1.0"
            ipAddress={baseUrl}
            isConnected={isConnected}
            onIpChange={handleIpChange}
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
