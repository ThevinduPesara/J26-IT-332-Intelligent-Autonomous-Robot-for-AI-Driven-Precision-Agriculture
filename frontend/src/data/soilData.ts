// Mock data for Soil NPK Monitoring page (/soil)
// Anyone with basic coding knowledge can easily edit these values!

export const soilData = {
  header: {
    title: "Soil NPK Diagnostics",
    sensorBadge: "ESP32 Probed Sensor Online",
    description:
      "Real-time electrochemical macronutrient analysis from AgriBot subsurface probe.",
  },
  macronutrients: [
    {
      id: "nitrogen",
      category: "MACRONUTRIENT",
      name: "Nitrogen",
      symbol: "(N)",
      value: "45.2",
      unit: "mg/kg",
      rangeText: "Range: 0 - 100 mg/kg",
      percentage: 45.2,
      status: "Optimal",
      statusType: "optimal", // 'optimal' or 'moderate'
      updatedTime: "Just now",
      targetRange: "40-60",
      barColor: "bg-emerald-900",
    },
    {
      id: "phosphorus",
      category: "MACRONUTRIENT",
      name: "Phosphorus",
      symbol: "(P)",
      value: "18.6",
      unit: "mg/kg",
      rangeText: "Range: 0 - 50 mg/kg",
      percentage: 37.2,
      status: "Moderate",
      statusType: "moderate",
      updatedTime: "Just now",
      targetRange: "20-40",
      barColor: "bg-amber-800",
    },
    {
      id: "potassium",
      category: "MACRONUTRIENT",
      name: "Potassium",
      symbol: "(K)",
      value: "124.5",
      unit: "mg/kg",
      rangeText: "Range: 0 - 200 mg/kg",
      percentage: 62.2,
      status: "Optimal",
      statusType: "optimal",
      updatedTime: "Just now",
      targetRange: "100-150",
      barColor: "bg-teal-700",
    },
  ],
  trendChart: {
    title: "24-Hour Nutrient Trend",
    subtitle: "Subsurface fluctuations recorded across Sector 4 testing zones.",
    legend: [
      { name: "N", color: "bg-emerald-900" },
      { name: "P", color: "bg-amber-800" },
      { name: "K", color: "bg-teal-700" },
    ],
    timeLabels: ["00:00 UTC", "06:00 UTC", "12:00 UTC", "18:00 UTC", "Now"],
  },
  sensorVsVision: {
    title: "Sensor vs. AI Vision",
    paragraph1:
      "Physical NPK readings are acquired via direct electrochemical soil contact probes embedded in the AgriBot chassis.",
    paragraph2:
      "These telemetry values are entirely separate from AI visual plant analysis, which assesses foliage discoloration and canopy stress optically via the top-mounted stereoscopic camera.",
    calibratedBadge: "Hardware Calibrated Daily",
  },
};
