// Mock data for AI Plant Detection page (/detection)
// Anyone with basic coding knowledge can easily edit these values!

export const detectionData = {
  summaryCards: [
    {
      id: "scanned",
      label: "TOTAL SCANNED",
      value: "1,428 Plants",
      iconName: "Crosshair",
      iconBg: "bg-emerald-100",
      iconColor: "text-emerald-700",
    },
    {
      id: "health",
      label: "HEALTHY INDEX",
      value: "88.4%",
      iconName: "Leaf",
      iconBg: "bg-emerald-100",
      iconColor: "text-emerald-700",
    },
    {
      id: "pests",
      label: "PEST ALERTS",
      value: "12 Active",
      iconName: "Bug",
      iconBg: "bg-red-100",
      iconColor: "text-red-700",
    },
    {
      id: "model",
      label: "MODEL VERSION",
      value: "ChilliNet v4.2",
      iconName: "Zap",
      iconBg: "bg-amber-100",
      iconColor: "text-amber-800",
    },
  ],
  insights: [
    {
      id: "nutrient",
      badgeLabel: "Nutrient Analysis",
      badgeType: "teal",
      metaText: "Updated 10m ago",
      title: "Nitrogen Depletion Detected",
      description:
        "Sector 4 exhibits mild chlorosis in lower canopy leaves. Recommended NPK adjustment: +15% nitrogen dosage during next fertigation cycle.",
      progress: 68,
      progressBarColor: "bg-teal-700",
    },
    {
      id: "pest",
      badgeLabel: "Pest Scouting",
      badgeType: "red",
      metaText: "Active Scan",
      title: "Aphid Activity in Row B",
      description:
        "AI Vision detected early-stage vector clustering near #PLT-883. Targeted organic neem oil application recommended within 24 hours.",
      progress: 75,
      progressBarColor: "bg-red-600",
    },
    {
      id: "growth",
      badgeLabel: "Growth Velocity",
      badgeType: "green",
      metaText: "Optimal Range",
      title: "+2.4cm Daily Canopy Spread",
      description:
        "Overall vegetative phase progressing 12% faster than seasonal baseline due to precise micro-climate irrigation tuning.",
      progress: 84,
      progressBarColor: "bg-emerald-700",
    },
  ],
  plantCards: [
    {
      id: "PLT-882",
      status: "Healthy",
      confidence: "98%",
      species: "Capsicum annuum L.",
      zone: "Zone A - Row 1",
      description:
        "Excellent chlorophyll index. Strong vascular structure with zero pest incidence.",
      scannedTime: "2 mins ago",
      imageUrl:
        "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "PLT-883",
      status: "Moderate",
      confidence: "94%",
      species: "Capsicum annuum L.",
      zone: "Zone A - Row 2",
      description:
        "Mild leaf margin chlorosis detected. Requires automated nitrogen boost via micro-irrigation.",
      scannedTime: "14 mins ago",
      imageUrl:
        "https://images.unsplash.com/photo-1592417817098-8f3d6eb228cc?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "PLT-884",
      status: "Poor",
      confidence: "97%",
      species: "Capsicum annuum L.",
      zone: "Zone B - Row 4",
      description:
        "Pest activity confirmed (Aphids). Leaf curling and stunted node development observed.",
      scannedTime: "25 mins ago",
      imageUrl:
        "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "PLT-885",
      status: "Healthy",
      confidence: "98%",
      species: "Capsicum annuum L.",
      zone: "Zone A - Row 3",
      description:
        "Vigorous early flower bud initiation. Foliage density and transpiration rate normal.",
      scannedTime: "32 mins ago",
      imageUrl:
        "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "PLT-886",
      status: "Moderate",
      confidence: "95%",
      species: "Capsicum annuum L.",
      zone: "Zone C - Row 1",
      description:
        "Water stress detected in peripheral canopy. Soil moisture probe shows 32% (Sub-optimal).",
      scannedTime: "40 mins ago",
      imageUrl:
        "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=600&q=80",
    },
    {
      id: "PLT-887",
      status: "Healthy",
      confidence: "99%",
      species: "Capsicum annuum L.",
      zone: "Zone A - Row 4",
      description:
        "Optimal stem diameter and internode spacing. Trichome density indicates robust natural defense.",
      scannedTime: "55 mins ago",
      imageUrl:
        "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?auto=format&fit=crop&w=600&q=80",
    },
  ],
};
