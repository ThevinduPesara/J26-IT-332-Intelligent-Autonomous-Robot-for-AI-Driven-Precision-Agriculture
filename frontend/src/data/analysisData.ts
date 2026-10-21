// Mock data for AgriBot AI & Telemetry Analysis page (/analysis)
// Anyone with basic coding knowledge can edit or extend these values!

export const analysisData = {
  header: {
    category: "ADVANCED TELEMETRY & AI METRICS",
    title: "System Performance & Field Analysis",
    description:
      "Comprehensive statistical analysis combining electrochemical soil diagnostics, AI crop yield predictions, and autonomous robot energy efficiency.",
    lastSync: "Updated: 5 mins ago",
  },
  kpiStats: [
    {
      id: "yield",
      label: "PROJECTED CROP YIELD",
      value: "+18.4%",
      subtext: "vs. conventional manual farming",
      badge: "Optimal",
      badgeType: "optimal",
      iconName: "TrendingUp",
    },
    {
      id: "coverage",
      label: "TOTAL FIELD COVERAGE",
      value: "96.2%",
      subtext: "14.2 of 14.8 hectares scanned",
      badge: "On Schedule",
      badgeType: "optimal",
      iconName: "Maximize2",
    },
    {
      id: "energy",
      label: "SOLAR ENERGY RATIO",
      value: "74.8%",
      subtext: "Self-sustaining autonomous run",
      badge: "+14W Surplus",
      badgeType: "optimal",
      iconName: "Zap",
    },
    {
      id: "healthAvg",
      label: "CANOPY HEALTH INDEX",
      value: "92.6",
      subtext: "AI confidence aggregate score",
      badge: "Grade A",
      badgeType: "optimal",
      iconName: "Sprout",
    },
  ],
  yieldFactors: [
    { name: "NPK Nutrient Balance", score: 91, status: "Optimal", color: "bg-emerald-700" },
    { name: "Pest & Weed Mitigation", score: 86, status: "Good", color: "bg-teal-700" },
    { name: "Soil Hydration Consistency", score: 78, status: "Moderate", color: "bg-amber-600" },
    { name: "Seed Spacing Uniformity", score: 95, status: "Excellent", color: "bg-emerald-800" },
  ],
  sectorComparison: [
    { sector: "Sector A (North Corridor)", plants: 420, health: "94.2%", soilScore: "Optimal", pestRisk: "Low (2%)" },
    { sector: "Sector B (Central Track)", plants: 512, health: "88.6%", soilScore: "Moderate", pestRisk: "Med (8%)" },
    { sector: "Sector C (South Wing)", plants: 310, health: "95.1%", soilScore: "Optimal", pestRisk: "Low (1%)" },
    { sector: "Sector D (Perimeter)", plants: 186, health: "84.3%", soilScore: "Deficient", pestRisk: "High (14%)" },
  ],
};
