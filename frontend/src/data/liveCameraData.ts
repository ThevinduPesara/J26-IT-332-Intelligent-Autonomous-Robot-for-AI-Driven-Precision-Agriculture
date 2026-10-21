// Mock data for Live Camera Page
// Any developer can easily adjust these telemetry values and camera settings!

export const liveCameraData = {
  cameraInfo: {
    name: "CAM-01: Chilli Plantation Sector B",
    resolutionFps: "1080p @ 30fps",
    irStatus: "IR Active",
    connectionStatus: "Connected",
    recDuration: "00:42:12",
    battery: "88%",
    signal: "Excellent",
    date: "18 OCT 2026, 10:45 AM",
    zoom: "1.5x",
    focus: "Auto",
    grid: "ON",
  },
  detectedBBoxes: [
    {
      id: "#104",
      confidence: "96.4%",
      label: "Capsicum annuum",
      x: "40%",
      y: "18%",
      width: "120px",
      height: "150px",
    },
    {
      id: "#105",
      confidence: "94.1%",
      label: "Seedling",
      x: "50%",
      y: "26%",
      width: "110px",
      height: "140px",
    },
  ],
  targetDetails: {
    statusBadge: "Locked",
    plantId: "#104",
    species: "Capsicum annuum",
    healthStatus: "Healthy",
    aiConfidence: "96.4%",
    timestamp: "14:22:08 UTC",
    diagnostics: {
      soilMoisture: "48% (Optimal)",
      npkIndex: "N: 120, P: 45, K: 85",
    },
  },
  metrics: [
    {
      id: "streams",
      title: "Active Streams",
      value: "4 Units Online",
      iconName: "Video",
    },
    {
      id: "accuracy",
      title: "Detection Accuracy",
      value: "98.2% Avg",
      iconName: "Crosshair",
    },
    {
      id: "storage",
      title: "Storage Buffer",
      value: "18.4 GB Free",
      iconName: "HardDrive",
    },
  ],
};
