"use client";

import React, { useState } from "react";
import NavigationHeader from "@/components/navigation/NavigationHeader";
import CableTrackMatrix from "@/components/navigation/CableTrackMatrix";
import MotorTelemetryCards from "@/components/navigation/MotorTelemetryCards";
import MovementControlsCard from "@/components/navigation/MovementControlsCard";
import { navigationData } from "@/data/navigationData";

/**
 * ROBOT NAVIGATION & MOVEMENT CONTROL PAGE (/navigation)
 * Fully modular and accessible for all development levels.
 */
export default function RobotNavigationPage() {
  const [currentPosition, setCurrentPosition] = useState(
    navigationData.trackMatrix.currentPosition
  );
  const [movementState, setMovementState] = useState(
    navigationData.trackMatrix.initialState
  );

  const handleMoveLeft = () => {
    setCurrentPosition((prev) => Math.max(prev - 5, 0));
    setMovementState("Moving Left");
  };

  const handleMoveRight = () => {
    setCurrentPosition((prev) =>
      Math.min(prev + 5, navigationData.trackMatrix.totalLength)
    );
    setMovementState("Moving Right");
  };

  const handleReturnHome = () => {
    setCurrentPosition(0);
    setMovementState("Stopped");
  };

  const handleEmergencyStop = () => {
    setMovementState("Stopped");
    alert("Emergency Brake Engaged! Robot stopped at current position.");
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Section */}
      <NavigationHeader
        category={navigationData.header.category}
        title={navigationData.header.title}
        stepperOnlineBadge={navigationData.header.stepperOnlineBadge}
        rssi={navigationData.header.rssi}
      />

      {/* 2. Main 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
        {/* Left Column (2 Cols): Cable Track Matrix & Motor Telemetry */}
        <div className="lg:col-span-2 space-y-6 flex flex-col justify-between">
          <CableTrackMatrix
            title={navigationData.trackMatrix.title}
            speed={navigationData.trackMatrix.initialSpeed}
            movementState={movementState}
            currentPosition={currentPosition}
            totalLength={navigationData.trackMatrix.totalLength}
            targetNode={navigationData.trackMatrix.targetNode}
            nodes={navigationData.trackMatrix.nodes}
          />

          <MotorTelemetryCards
            stepperMotorLoad={navigationData.telemetry.stepperMotorLoad}
            driverTemperature={navigationData.telemetry.driverTemperature}
          />
        </div>

        {/* Right Column (1 Col): Movement Controls */}
        <div className="lg:col-span-1">
          <MovementControlsCard
            title={navigationData.controls.title}
            description={navigationData.controls.description}
            statusState={movementState}
            emergencyNotice={navigationData.controls.emergencyNotice}
            onMoveLeft={handleMoveLeft}
            onMoveRight={handleMoveRight}
            onReturnHome={handleReturnHome}
            onEmergencyStop={handleEmergencyStop}
          />
        </div>
      </div>
    </div>
  );
}
