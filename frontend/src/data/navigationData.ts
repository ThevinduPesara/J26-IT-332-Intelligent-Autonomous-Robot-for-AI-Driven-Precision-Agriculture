// Mock data for Robot Navigation page (/navigation)
// Anyone with basic coding knowledge can easily edit these values!

export const navigationData = {
  header: {
    category: "AUTONOMOUS TRACK SYSTEM",
    title: "Robot Navigation & Movement Control",
    stepperOnlineBadge: "ESP32-CAM & Stepper Online",
    rssi: "-64 dBm",
  },
  trackMatrix: {
    title: "100m Cable Track Matrix",
    initialSpeed: "0.5 m/s",
    initialState: "Stopped", // "Stopped", "Moving Left", "Moving Right"
    currentPosition: 45.2, // meters
    totalLength: 100, // meters
    progress: 45.2,
    targetNode: "Node #3 (50m)",
    nodes: [
      { label: "0m", position: 0 },
      { label: "20m", position: 20 },
      { label: "40m", position: 40 },
      { label: "60m", position: 60 },
      { label: "80m", position: 80 },
      { label: "100m", position: 100 },
    ],
  },
  telemetry: {
    stepperMotorLoad: {
      value: "1.2 A",
      status: "Optimal",
    },
    driverTemperature: {
      value: "38.4 °C",
      status: "Normal",
    },
  },
  controls: {
    title: "Movement Controls",
    description: "Manual override and precise positioning controls for field operations.",
    emergencyNotice: "Emergency brake engages immediately",
  },
};
