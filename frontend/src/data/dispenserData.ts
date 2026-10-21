// Mock data for Seed Dispenser Control page (/dispenser)
// Anyone with basic coding knowledge can easily edit the values here!

export const dispenserData = {
  header: {
    title: "Seed Dispenser Control",
    description:
      "Manage autonomous seed delivery systems, adjust payload rates, and verify hardware relay connectivity.",
    protocol: {
      label: "Hardware Protocol",
      value: "MQTT / IoT Relay v2.4",
    },
  },
  primaryDispenser: {
    title: "Primary Pneumatic Dispenser",
    unitId: "AG-DISP-04",
    hopperCap: "85%",
    statusBadge: "Standby",
    metrics: [
      {
        id: "rate",
        label: "Dispense Rate",
        value: "42 seeds / sec",
      },
      {
        id: "activation",
        label: "Last Activation",
        value: "Today, 08:42 AM",
      },
      {
        id: "temp",
        label: "Actuator Temp",
        value: "34.2 °C",
        statusTag: "Nominal",
      },
    ],
    actuationBox: {
      title: "Master Hardware Actuation",
      description: "Toggles physical seed drop mechanisms via IoT relay.",
      initialState: false, // false = OFF, true = ON
    },
  },
  relayStatus: {
    title: "IoT Relay Status",
    connectionText: "IoT Relay Connected",
    statusBadge: "Online",
    signalStrengthRssi: "-64 dBm",
    signalPercentage: 78,
    packetLatency: "18 ms",
    relayFirmware: "v4.1.2-mqtt",
  },
  hopperDiagnostics: {
    title: "Hopper Diagnostics",
    percentage: 85,
    statusText: "Seed Level Optimal",
    coverageText: "Estimated coverage remaining: 14.2 acres before next refill.",
    autoCalibrationStatus: "Active",
  },
  safetyNotice: {
    title: "Hardware Safety Notice",
    description:
      "Physical hardware actuation requires a continuous, stable connection to the IoT backend. Disabling the dispenser mid-cycle will automatically park the pneumatic valve to prevent seed clogging or back-pressure damage in the delivery tubes.",
  },
};
