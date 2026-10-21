"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import Image from "next/image";
import {
  ArrowLeft,
  ArrowRight,
  OctagonX,
  Radio,
  Wifi,
  WifiOff,
  AlertTriangle,
  RefreshCw,
  Activity,
  ShieldAlert,
  SlidersHorizontal,
  Cpu,
  Keyboard,
  Signal,
  Check,
} from "lucide-react";
import cableRobotService, {
  ConnectionState,
  MovementCommand,
  Esp32StatusResponse,
} from "@/services/cableRobotService";
import "./CableRobotControl.css";

interface CableRobotControlProps {
  onMovementChange?: (movement: string) => void;
  className?: string;
}

export default function CableRobotControl({
  onMovementChange,
  className = "",
}: CableRobotControlProps) {
  const [connectionState, setConnectionState] =
    useState<ConnectionState>("connecting");
  const [connectionMessage, setConnectionMessage] =
    useState<string>("Connecting to ESP32 Web Server...");
  const [espStatus, setEspStatus] = useState<Esp32StatusResponse | null>(null);
  const [activeCommand, setActiveCommand] = useState<MovementCommand>("STOP");
  const [isPressingLeft, setIsPressingLeft] = useState<boolean>(false);
  const [isPressingRight, setIsPressingRight] = useState<boolean>(false);
  const [customEspUrl, setCustomEspUrl] = useState<string>("");
  const [showConfig, setShowConfig] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  const activeKeyRef = useRef<string | null>(null);

  // Stop movement safely
  const handleStopMovement = useCallback(async () => {
    setIsPressingLeft(false);
    setIsPressingRight(false);
    activeKeyRef.current = null;

    // Only fire network STOP if the robot was actually moving or requested
    if (cableRobotService.getActiveCommand() !== "STOP") {
      setActiveCommand("STOP");
      onMovementChange?.("Stopped");
      await cableRobotService.stopMovement();
    } else {
      setActiveCommand("STOP");
    }
  }, [onMovementChange]);

  // Start continuous movement safely
  const handleStartMovement = useCallback(
    async (direction: "LEFT" | "RIGHT") => {
      if (direction === "LEFT") {
        setIsPressingLeft(true);
        setIsPressingRight(false);
      } else {
        setIsPressingRight(true);
        setIsPressingLeft(false);
      }

      const sent = await cableRobotService.startContinuousMovement(direction);
      if (sent) {
        setActiveCommand(direction);
        onMovementChange?.(
          direction === "LEFT" ? "Moving Left" : "Moving Right"
        );
      } else {
        handleStopMovement();
      }
    },
    [handleStopMovement, onMovementChange]
  );

  // Initialize service callbacks and lifecycle
  useEffect(() => {
    setCustomEspUrl(cableRobotService.getBaseUrl());

    cableRobotService.setCallbacks({
      onConnectionChange: (state, message) => {
        setConnectionState(state);
        if (message) setConnectionMessage(message);
        if (state !== "connected") {
          setIsPressingLeft(false);
          setIsPressingRight(false);
          setActiveCommand("STOP");
        }
      },
      onStatusUpdate: (status) => {
        setEspStatus(status);
      },
      onError: (err) => {
        setConnectionMessage(err.message || "ESP32 communication error");
      },
    });

    cableRobotService.start();

    // Safety: window blur event must halt robot movement immediately
    const handleWindowBlur = () => {
      handleStopMovement();
    };

    // Keyboard support: Left Arrow (LEFT), Right Arrow (RIGHT), Escape (STOP)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.repeat) return;

      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }

      if (e.key === "ArrowLeft") {
        e.preventDefault();
        activeKeyRef.current = "ArrowLeft";
        handleStartMovement("LEFT");
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        activeKeyRef.current = "ArrowRight";
        handleStartMovement("RIGHT");
      } else if (e.key === "Escape" || e.key === " ") {
        e.preventDefault();
        handleStopMovement();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (
        (e.key === "ArrowLeft" && activeKeyRef.current === "ArrowLeft") ||
        (e.key === "ArrowRight" && activeKeyRef.current === "ArrowRight")
      ) {
        activeKeyRef.current = null;
        handleStopMovement();
      }
    };

    window.addEventListener("blur", handleWindowBlur);
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    return () => {
      window.removeEventListener("blur", handleWindowBlur);
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
      cableRobotService.stopMovement();
      cableRobotService.stop();
    };
  }, [handleStartMovement, handleStopMovement]);

  const isConnected = connectionState === "connected";
  const baseUrl = cableRobotService.getBaseUrl();

  const handleSaveIp = () => {
    if (customEspUrl.trim()) {
      cableRobotService.setBaseUrl(customEspUrl.trim());
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2000);
    }
  };

  return (
    <div
      className={`cable-robot-panel bg-white rounded-3xl p-6 md:p-7 border border-slate-200/90 shadow-sm flex flex-col justify-between space-y-6 ${className}`}
    >
      {/* 1. Header Section */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-black tracking-wider text-emerald-800 uppercase">
              CABLE ROBOT CONTROLLER
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-semibold border border-slate-200">
              ESP32 HTTP REST
            </span>
          </div>

          {/* Connection Status Indicator */}
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border transition ${
                isConnected
                  ? "bg-emerald-50 text-emerald-700 border-emerald-300 shadow-2xs"
                  : connectionState === "connecting"
                  ? "bg-amber-50 text-amber-700 border-amber-300 animate-pulse"
                  : "bg-rose-50 text-rose-700 border-rose-300"
              }`}
            >
              {isConnected ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  <Wifi className="w-3.5 h-3.5" />
                  <span>ESP32 Online</span>
                </>
              ) : connectionState === "connecting" ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-3.5 h-3.5" />
                  <span>ESP32 Offline</span>
                </>
              )}
            </span>

            <button
              onClick={() => setShowConfig(!showConfig)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
              title="ESP32 IP Configuration"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        <h2 className="text-lg font-black text-slate-800 tracking-tight">
          Suspension Cable Robot Motor Control
        </h2>
        <p className="text-xs text-slate-500 mt-1 leading-relaxed">
          Direct low-latency HTTP REST commands (POST /api/command) with 250ms safety heartbeat to ESP32 Web Server.
        </p>

        {/* Dynamic ESP32 IP Configuration Drawer */}
        {showConfig && (
          <div className="mt-3 p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-700">ESP32 Device Endpoint:</span>
              <span className="font-mono text-[11px] text-emerald-800 font-bold">{baseUrl}</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="http://192.168.x.x"
                value={customEspUrl}
                onChange={(e) => setCustomEspUrl(e.target.value)}
                className="flex-1 px-3 py-1.5 rounded-xl border border-slate-300 bg-white font-mono text-xs focus:outline-emerald-600"
              />
              <button
                onClick={handleSaveIp}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-emerald-800 text-white font-bold text-xs hover:bg-emerald-900 transition cursor-pointer"
              >
                {savedSuccess ? <Check className="w-3.5 h-3.5" /> : null}
                {savedSuccess ? "Saved!" : "Set IP"}
              </button>
            </div>
            <p className="text-[10px] text-slate-400">
              Tip: Check the IP shown on ESP32 Serial Monitor (e.g. http://192.168.1.50) and set it here.
            </p>
          </div>
        )}
      </div>

      {/* 2-Column Responsive Body for full-width dashboard layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        {/* Left Column: Robot Image Illustration with Telemetry Overlay */}
        <div className="relative rounded-2xl overflow-hidden border border-slate-200/90 bg-slate-950 min-h-[280px] lg:min-h-[360px] flex items-center justify-center shadow-inner group">
          <Image
            src="/cable_robot_illustration.svg"
            alt="AgriBot Cable Suspended Precision Agriculture Robot"
            fill
            priority
            sizes="(max-width: 1024px) 100vw, 50vw"
            className="object-cover transition-transform duration-700 group-hover:scale-[1.02]"
          />

          {/* Active Direction Pulse Overlay */}
          {activeCommand !== "STOP" && (
            <div
              className={`absolute inset-0 bg-emerald-500/10 backdrop-blur-[1px] flex items-center justify-center pointer-events-none transition-opacity duration-300 ${
                activeCommand === "LEFT" ? "justify-start pl-8" : "justify-end pr-8"
              }`}
            >
              <div className="bg-emerald-950/85 border border-emerald-400 text-emerald-300 px-4 py-2 rounded-2xl flex items-center gap-2 font-mono font-bold text-xs shadow-lg animate-pulse">
                <Radio className="w-4 h-4 text-emerald-400" />
                <span>PULSING `{activeCommand}` TO MOTOR DRIVER</span>
              </div>
            </div>
          )}

          {/* Telemetry pill overlays on image */}
          <div className="absolute top-3 left-3 bg-black/75 backdrop-blur-md px-3 py-1.5 rounded-xl text-[11px] font-mono text-white/90 border border-white/10 flex items-center gap-2 shadow-md">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>
              Status: <b className="text-emerald-300">{espStatus?.status || (isConnected ? "READY" : "WAITING")}</b>
            </span>
            {espStatus?.wifiRSSI && (
              <span className="flex items-center gap-1 text-[10px] text-slate-300 pl-1 border-l border-white/20">
                <Signal className="w-3 h-3 text-teal-400" />
                {espStatus.wifiRSSI} dBm
              </span>
            )}
          </div>

          <div className="absolute bottom-3 right-3 bg-black/75 backdrop-blur-md px-2.5 py-1 rounded-lg text-[10px] font-mono text-slate-300 border border-white/10 flex items-center gap-1.5">
            <Keyboard className="w-3 h-3 text-slate-400" />
            <span>Arrows / Hold to move • Esc to stop</span>
          </div>
        </div>

        {/* Right Column: Status Bar, Controls, Emergency Stop & Safety Notice */}
        <div className="flex flex-col justify-between space-y-4">
          {/* Status Bar & Connection Alert */}
          <div className="space-y-2">
            <div className="bg-slate-50/90 rounded-2xl p-4 border border-slate-200/80 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm ${
                    activeCommand === "STOP"
                      ? "bg-slate-200 text-slate-700"
                      : "bg-emerald-600 text-white animate-pulse"
                  }`}
                >
                  <Activity className="w-5 h-5" />
                </div>
                <div>
                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Robot Motion Status
                  </span>
                  <span
                    className={`text-base font-black tracking-tight ${
                      activeCommand === "STOP"
                        ? "text-slate-700"
                        : "text-emerald-700"
                    }`}
                  >
                    {activeCommand === "STOP"
                      ? "Stopped / Stationary"
                      : `Traversing ${activeCommand} (${
                          activeCommand === "LEFT" ? "← Left" : "Right →"
                        })`}
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  Heartbeat Interval
                </span>
                <span className="text-xs font-mono font-bold text-slate-600">
                  {activeCommand !== "STOP" ? "250ms Active" : "Standby (700ms cutoff)"}
                </span>
              </div>
            </div>

            {/* Offline notice */}
            {!isConnected && (
              <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 flex items-start gap-2.5 text-amber-800 text-xs">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
                <div className="flex-1">
                  <span className="font-bold block">ESP32 Not Reachable</span>
                  <p className="text-[11px] text-amber-700 mt-0.5">
                    {connectionMessage}. Make sure ESP32 is connected to Wi-Fi and its IP matches <b>{baseUrl}</b>.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Action Controls: Press & Hold LEFT / RIGHT and STOP ROBOT */}
          <div className="space-y-3 pt-2">
            <div className="grid grid-cols-2 gap-4">
              {/* MOVE LEFT BUTTON */}
              <button
                type="button"
                disabled={!isConnected}
                onMouseDown={() => handleStartMovement("LEFT")}
                onMouseUp={handleStopMovement}
                onMouseLeave={handleStopMovement}
                onClick={() => {
                  handleStartMovement("LEFT");
                  setTimeout(() => handleStopMovement(), 400);
                }}
                onTouchStart={(e) => {
                  e.preventDefault();
                  handleStartMovement("LEFT");
                }}
                onTouchEnd={(e) => {
                  e.preventDefault();
                  handleStopMovement();
                }}
                className={`cable-robot-control-btn group flex flex-col items-center justify-center gap-2 py-4 px-4 rounded-2xl font-bold text-xs transition-all duration-150 shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none ${
                  isPressingLeft
                    ? "bg-emerald-900 text-white scale-[0.98] ring-4 ring-emerald-500/40"
                    : "bg-[#14532d] hover:bg-emerald-900 text-white active:scale-95"
                }`}
              >
                <ArrowLeft
                  className={`w-6 h-6 transition-transform ${
                    isPressingLeft
                      ? "-translate-x-1"
                      : "group-hover:-translate-x-0.5"
                  }`}
                />
                <div className="text-center">
                  <span className="block text-sm font-extrabold">MOVE LEFT</span>
                  <span className="text-[10px] text-emerald-200/80 font-normal">
                    {isPressingLeft ? "Moving Left..." : "Hold or Click / [←]"}
                  </span>
                </div>
              </button>

              {/* MOVE RIGHT BUTTON */}
              <button
                type="button"
                disabled={!isConnected}
                onMouseDown={() => handleStartMovement("RIGHT")}
                onMouseUp={handleStopMovement}
                onMouseLeave={handleStopMovement}
                onClick={() => {
                  handleStartMovement("RIGHT");
                  setTimeout(() => handleStopMovement(), 400);
                }}
                onTouchStart={(e) => {
                  e.preventDefault();
                  handleStartMovement("RIGHT");
                }}
                onTouchEnd={(e) => {
                  e.preventDefault();
                  handleStopMovement();
                }}
                className={`cable-robot-control-btn group flex flex-col items-center justify-center gap-2 py-4 px-4 rounded-2xl font-bold text-xs transition-all duration-150 shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none ${
                  isPressingRight
                    ? "bg-emerald-900 text-white scale-[0.98] ring-4 ring-emerald-500/40"
                    : "bg-[#14532d] hover:bg-emerald-900 text-white active:scale-95"
                }`}
              >
                <ArrowRight
                  className={`w-6 h-6 transition-transform ${
                    isPressingRight ? "translate-x-1" : "group-hover:translate-x-0.5"
                  }`}
                />
                <div className="text-center">
                  <span className="block text-sm font-extrabold">MOVE RIGHT</span>
                  <span className="text-[10px] text-emerald-200/80 font-normal">
                    {isPressingRight ? "Release to Stop" : "Press & Hold / [→]"}
                  </span>
                </div>
              </button>
            </div>

            {/* STOP ROBOT BUTTON */}
            <button
              type="button"
              onClick={handleStopMovement}
              className="w-full flex items-center justify-center gap-2 py-4 px-6 rounded-2xl bg-[#b91c1c] hover:bg-red-800 active:bg-red-900 text-white font-black text-sm shadow-md shadow-red-700/20 active:scale-[0.98] transition cursor-pointer select-none"
            >
              <OctagonX className="w-5 h-5 fill-current" />
              <span>STOP ROBOT [ESC]</span>
            </button>

            {/* Safety Notice Footer */}
            <div className="pt-1 text-center space-y-0.5">
              <div className="flex items-center justify-center gap-1.5 text-[11px] text-slate-400 font-medium">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                <span>Software STOP does not substitute physical e-stop switches.</span>
              </div>
              <p className="text-[10px] text-slate-400">
                ESP32 firmware independently enforces a 700ms safety timeout if frontend heartbeat ceases.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
