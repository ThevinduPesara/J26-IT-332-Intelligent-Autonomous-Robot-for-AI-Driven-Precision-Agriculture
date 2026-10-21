// Research Project - 4 Core Research Models Mock Data
// Easy to modify by any team member!

export const researchModelsData = {
  // Model 1: Chilli NPK Requirement Predictor
  chilliRequirement: {
    title: "Chilli Crop NPK Requirement Predictor",
    badge: "AI Agronomy Model v3.1",
    cropStage: "Early Flowering Stage (Day 48)",
    targetSpecies: "Capsicum annuum L. (Hot Pepper / Chilli)",
    summary:
      "Predicts optimal macronutrient requirements tailored to chilli plant phenological stages, soil pH, and environmental transpiration rates.",
    requirements: [
      { element: "Nitrogen (N)", target: 160, unit: "mg/kg", importance: "Canopy and vegetative leaf support", color: "text-emerald-700", bg: "bg-emerald-50" },
      { element: "Phosphorus (P)", target: 40, unit: "mg/kg", importance: "Root anchorage and early flower bud induction", color: "text-amber-800", bg: "bg-amber-50" },
      { element: "Potassium (K)", target: 180, unit: "mg/kg", importance: "Fruit sizing, drought resistance, and capsaicin synthesis", color: "text-teal-700", bg: "bg-teal-50" },
    ],
    growthStages: [
      { stage: "Seedling (0-20d)", n: "80 mg/kg", p: "30 mg/kg", k: "90 mg/kg", active: false },
      { stage: "Vegetative (21-40d)", n: "130 mg/kg", p: "35 mg/kg", k: "140 mg/kg", active: false },
      { stage: "Flowering (41-65d)", n: "160 mg/kg", p: "40 mg/kg", k: "180 mg/kg", active: true },
      { stage: "Fruiting (66-90d)", n: "140 mg/kg", p: "30 mg/kg", k: "220 mg/kg", active: false },
    ],
  },

  // Model 2: Soil Sensor vs. NPK Deficiency Comparator
  soilComparison: {
    title: "Real-time Soil Sensor vs. NPK Deficiency Comparator",
    badge: "Sensor-AI Calibration Engine",
    probeId: "ESP32-NPK-SUB-04",
    lastReadingTime: "Today, 14:32:01 UTC",
    summary:
      "Cross-references live subsurface electrochemical probe values with optimal target demands to compute precise micro-fertilizer dosing.",
    comparisonTable: [
      {
        nutrient: "Nitrogen (N)",
        currentReading: 45.2,
        requiredTarget: 160.0,
        deficit: 114.8,
        unit: "mg/kg",
        status: "High Deficit",
        statusColor: "bg-red-100 text-red-800",
        recommendedDose: "+11.4 g / m² (Urea formulation)",
      },
      {
        nutrient: "Phosphorus (P)",
        currentReading: 18.6,
        requiredTarget: 40.0,
        deficit: 21.4,
        unit: "mg/kg",
        status: "Moderate Deficit",
        statusColor: "bg-amber-100 text-amber-800",
        recommendedDose: "+4.2 g / m² (TSP formulation)",
      },
      {
        nutrient: "Potassium (K)",
        currentReading: 124.5,
        requiredTarget: 180.0,
        deficit: 55.5,
        unit: "mg/kg",
        status: "Mild Deficit",
        statusColor: "bg-emerald-100 text-emerald-800",
        recommendedDose: "+5.5 g / m² (MOP formulation)",
      },
    ],
  },

  // Model 3: Paddy (වී වගාව) Crop Gap & Canopy Discontinuity Detector
  paddyGap: {
    title: "Paddy Crop Gap & Seedling Discontinuity Detector",
    badge: "PaddyVision Semantic Segmentation",
    cropType: "Oryza sativa (Paddy / Rice)",
    summary:
      "Segments paddy-field images into existing plants, soil, and weeds, then summarizes class coverage and model confidence. This API does not generate individual gap counts or robot coordinates.",
  },

  // Model 4: Precise Pest Count & Multi-Class Infestation Quantifier
  pestCount: {
    title: "Precise Pest Count & Infestation Quantifier",
    badge: "YOLOv8-PestDensity v2.4",
    scanTarget: "Capsicum annuum Leaf Canopy Node #42",
    scanTimestamp: "Scanned 4 mins ago",
    totalPestCount: 64,
    infestationLevel: "Moderate Infestation",
    confidenceAvg: "96.2%",
    summary:
      "Performs high-resolution microscopic counting of individual insect bodies per leaf/cluster, eliminating vague estimations with exact counts.",
    pestBreakdown: [
      {
        species: "Aphids (Aphis gossypii)",
        count: 47,
        percentage: 73.4,
        typicalLocation: "Underside of young terminal leaves",
        risk: "High Risk (Sap drainage & virus vector)",
        color: "bg-red-600",
      },
      {
        species: "Chilli Thrips (Scirtothrips dorsalis)",
        count: 12,
        percentage: 18.8,
        typicalLocation: "Flower buds and developing calyx",
        risk: "Moderate Risk (Foliage curling)",
        color: "bg-amber-600",
      },
      {
        species: "Broad Mites (Polyphagotarsonemus)",
        count: 5,
        percentage: 7.8,
        typicalLocation: "Lower shaded leaf surfaces",
        risk: "Low / Contained Risk",
        color: "bg-teal-600",
      },
    ],
    recommendedSpraying: {
      organicFormulation: "Cold-pressed Neem Oil (0.5%) + Horticultural Soap",
      targetVolume: "45 ml / sector plot",
      status: "Ready for Automated Precision Spray Dispenser",
    },
  },
};
