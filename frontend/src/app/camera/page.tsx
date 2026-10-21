import React from "react";
import LiveFeedPlayer from "@/components/camera/LiveFeedPlayer";
import TargetDetailsCard from "@/components/camera/TargetDetailsCard";
import CameraMetricsRow from "@/components/camera/CameraMetricsRow";
import { liveCameraData } from "@/data/liveCameraData";

export const metadata = {
  title: "Live Camera & AI Plant Target - AgriBot IoT",
};

/**
 * LIVE CAMERA PAGE (/camera)
 * Modularized for simple editing and extension.
 */
export default function LiveCameraPage() {
  return (
    <div className="space-y-6">
      {/* Top Main Section: 2/3 Live Video Feed & 1/3 Target Diagnostics Card */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left: 2 Columns for Live Camera Video Feed */}
        <div className="lg:col-span-2">
          <LiveFeedPlayer
            cameraInfo={liveCameraData.cameraInfo}
            detectedBBoxes={liveCameraData.detectedBBoxes}
          />
        </div>

        {/* Right: 1 Column for Target Details Close-up and Controls */}
        <div className="lg:col-span-1">
          <TargetDetailsCard target={liveCameraData.targetDetails} />
        </div>
      </section>

      {/* Bottom Section: Active Streams, Detection Accuracy, Storage Buffer */}
      <section>
        <CameraMetricsRow metrics={liveCameraData.metrics} />
      </section>
    </div>
  );
}
