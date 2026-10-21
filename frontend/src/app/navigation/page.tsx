"use client";

import React, { useState } from "react";
import NavigationHeader from "@/components/navigation/NavigationHeader";
import CableTrackMatrix from "@/components/navigation/CableTrackMatrix";
import CableRobotControl from "@/components/CableRobot/CableRobotControl";
import { navigationData } from "@/data/navigationData";

/**
 * ROBOT NAVIGATION & MOVEMENT CONTROL PAGE (/navigation)
 * Full-width layout featuring the 100m Cable Track Matrix and Cable Robot Controller.
 */
export default function RobotNavigationPage() {
  const [currentPosition, setCurrentPosition] = useState(
    navigationData.trackMatrix.currentPosition
  );
  const [movementState, setMovementState] = useState(
    navigationData.trackMatrix.initialState
  );

  return (
    <div className="space-y-6">
      {/* 1. Header Section */}
      <NavigationHeader
        category={navigationData.header.category}
        title={navigationData.header.title}
        stepperOnlineBadge={navigationData.header.stepperOnlineBadge}
        rssi={navigationData.header.rssi}
      />

      {/* 2. Cable Track Matrix spanning full width across the page */}
      <div className="w-full">
        <CableTrackMatrix
          title={navigationData.trackMatrix.title}
          speed={
            movementState === "Stopped"
              ? "0.0 m/s"
              : navigationData.trackMatrix.initialSpeed
          }
          movementState={movementState}
          currentPosition={currentPosition}
          totalLength={navigationData.trackMatrix.totalLength}
          targetNode={navigationData.trackMatrix.targetNode}
          nodes={navigationData.trackMatrix.nodes}
        />
      </div>

      {/* 3. Dedicated Hardware Cable Robot ESP32 Controller spanning full width */}
      <div className="w-full">
        <CableRobotControl
          onMovementChange={(state) => {
            setMovementState(state);
            if (state === "Moving Left") {
              setCurrentPosition((prev) => Math.max(prev - 2, 0));
            } else if (state === "Moving Right") {
              setCurrentPosition((prev) =>
                Math.min(prev + 2, navigationData.trackMatrix.totalLength)
              );
            }
          }}
        />
      </div>
    </div>
  );
}

