// This file holds the mock data for the AgriBot IoT Dashboard.
// Anyone with basic coding knowledge can edit the values below to change what appears on the dashboard!

export const dashboardData = {
  robotInfo: {
    unitName: "Cable Robot Unit #01",
    sector: "Sector B-3",
    statusBadge: "Autonomous Mode Active",
    description:
      "Currently servicing Sector B-3. Real-time cable tension nominal, solar array generating optimal output. All autonomous routines executing on schedule.",
  },
  power: {
    percentage: 88,
    solarChargeRate: "+14W Solar Charge",
    voltage: "25.4 V",
    estimatedRuntime: "6h 45m",
  },
  stats: [
    {
      id: "state",
      label: "SYSTEM STATE",
      value: "Online",
      subtext: "Firmware v2.4.1-stable",
      statusColor: "emerald", // 'emerald' means active/green
      iconName: "Bot",
    },
    {
      id: "nav",
      label: "POSITION & NAV",
      value: "45.2m",
      subtext: "(Sector B-3)",
      badge: "Moving Left",
      iconName: "Navigation",
    },
    {
      id: "optical",
      label: "OPTICAL SENSOR",
      value: "Connected",
      subtext: "HD 1080p @ 30fps • IR Active",
      iconName: "Video",
    },
    {
      id: "plants",
      label: "AI PLANT COUNT",
      value: "142 plants",
      subtext: "98.4% Health Index Avg",
      iconName: "Crosshair",
    },
  ],
  cableTrack: {
    title: "Plantation Cable Track Overview",
    spanText: "Total Span: 100m • Real-time winch telemetry",
    statusText: "Normal",
    currentPosition: 45.2, // meters
    totalLength: 100, // meters
    winchSpeed: "0.4 m/s",
    tensionLoad: "14.2 N",
    motorTemp: "38.4°C",
  },
  soilNutrients: {
    statusBadge: "Optimal",
    nutrients: [
      { name: "Nitrogen (N)", value: 140, max: 200, unit: "mg/kg", color: "bg-emerald-900" },
      { name: "Phosphorus (P)", value: 45, max: 100, unit: "mg/kg", color: "bg-teal-700" },
      { name: "Potassium (K)", value: 210, max: 300, unit: "mg/kg", color: "bg-emerald-400" },
    ],
  },
  seedDispenser: {
    unitStatus: "OFF", // 'ON' or 'OFF'
  },
  recentActivity: [
    {
      id: 1,
      title: "Waypoint Sector B-3 Reached",
      description: "Autonomous navigation sequence completed successfully.",
      time: "10:42 AM",
      icon: "CheckCircle2",
      iconColor: "text-emerald-500",
      bgColor: "bg-emerald-50",
    },
    {
      id: 2,
      title: "AI Plant Detection Scan",
      description: "Detected 12 new sprouting tomato seedlings. Tagged coordinates.",
      time: "10:38 AM",
      icon: "Crosshair",
      iconColor: "text-teal-600",
      bgColor: "bg-teal-50",
    },
    {
      id: 3,
      title: "Solar Panel Alignment Adjusted",
      description: "Optimal sunlight angle locked (+14W peak efficiency).",
      time: "10:15 AM",
      icon: "Zap",
      iconColor: "text-emerald-500",
      bgColor: "bg-emerald-50",
    },
  ],
};
