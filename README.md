# 🌾 AgriBot (J26-IT-332)

## Intelligent Autonomous Robot for AI-Driven Precision Agriculture

An autonomous cable-suspended robotic platform integrating deep learning, computer vision, and IoT telemetry to deliver real-time crop health monitoring, phenological stage tracking, soil nutrient deficiency estimation, multi-class pest quantification, and automated paddy field gap seeding.

---

## 👥 Research Team & Contributions

| Student ID | Name                         | Research Component / Specialization                                                       |
| ---------- | ---------------------------- | ----------------------------------------------------------------------------------------- |
| IT23311640 | V.G.L. Sasmitha              | **Chilli Plant Detection & Growth Stage Estimation** (YOLOv8 & NPK Stage Profiling)       |
| IT23312630 | H.K.M. Kavishan              | **Soil Sensor vs. Deficiency Comparator** (NutrientOS & Micro-Fertilizer Dosing)          |
| IT23284470 | Senanayake Y.M.              | **Paddy Crop Gap Detection & Seed Dispenser Control** (PaddyVision Semantic Segmentation) |
| IT23275324 | G.A.T. Pesara                | **Precise Pest Count & Infestation Quantifier** (ChilliGuard Vision Multi-Class YOLOv8)   |

---

## 🌟 System Overview

Modern agriculture faces severe challenges including unpredictable yields, overuse of chemical inputs, labor shortages, and delayed pest or disease mitigation. **AgriBot (J26-IT-332)** addresses these challenges by introducing an end-to-end intelligent agricultural robotic ecosystem tailored for high-value crops (chilli) and staple grain cultivation (paddy).

Suspended on a low-energy, zero-soil-compaction plantation cable track, the autonomous robotic payload travels along crop rows to perform high-resolution optical inspection and soil sensing. The ecosystem is orchestrated through a centralized **Next.js 16** real-time mission dashboard communicating with four specialized **FastAPI** deep learning backends and an **MQTT-driven ESP32** embedded locomotion controller.

By replacing broad guesswork with micro-targeted agronomical interventions, AgriBot empowers farmers to reduce chemical footprint, optimize water and fertilizer efficiency, and safeguard crop yield.

---

## 🎯 Problem Statement

Traditional agricultural practices and current field scouting tools suffer from critical shortcomings:

- **Destructive Ground Vehicles:** Heavy tractors and wheeled agricultural rovers cause soil compaction, damage fragile plant root systems, and struggle over muddy, waterlogged paddy terrain.
- **Imprecise Fertilizer Application:** Blanket broadcasting of solid fertilizers leads to excessive nitrogen/phosphorus runoff, soil degradation, and high economic waste without addressing localized soil nutrient deficits.
- **Delayed Pest Infestation Response:** Manual insect scouting is labor-intensive and subjective, often identifying pest attacks only after significant foliage damage and virus transmission have occurred.
- **Canopy Gaps in Paddy Fields:** Gaps in rice seedling lines reduce maximum yield potential and allow aggressive weed colonization if not identified and re-seeded promptly.
- **Fragmented Tooling:** Existing digital farming systems operate in silos without coupling real-time AI perception to physical field actuators.

**AgriBot** unifies non-invasive cable suspension robotics, real-time computer vision inference, electrochemical soil sensing, and robotic dispenser actuation into a cohesive, automated field platform.

---

## 🧩 Core Research Components

```
                                  ┌───────────────────────────────────────────────┐
                                  │      Next.js 16 Mission Control Dashboard     │
                                  │            (http://localhost:3000)            │
                                  └───────┬───────────────────────────────┬───────┘
                                          │                               │
                 REST API (Port 8000/8501/8002/8003)              MQTT (WebSocket / TCP 1883)
                                          │                               │
       ┌──────────────────┬───────────────┴───────────────┬───────────────┴───────────────────┐
       ▼                  ▼                               ▼                                   ▼
┌──────────────┐   ┌──────────────┐                ┌──────────────┐                    ┌──────────────┐
│ Model 1      │   │ Model 2      │                │ Model 3      │                    │ Model 4      │
│ Chilli Plant │   │ NutrientOS   │                │ ChilliGuard  │                    │ PaddyVision  │
│ Detection &  │   │ Soil NPK     │                │ Pest Vision  │                    │ Semantic     │
│ Phenology    │   │ Deficiency   │                │ Density      │                    │ Segmentation │
│ (Port 8000)  │   │ (Port 8501)  │                │ (Port 8002)  │                    │ (Port 8003)  │
└──────────────┘   └──────────────┘                └──────────────┘                    └──────────────┘
                                                                                              │
                                                                               Actuator Command via MQTT
                                                                                              ▼
                                                                                       ┌──────────────┐
                                                                                       │ ESP32 Cable  │
                                                                                       │ Robot & Seed │
                                                                                       │ Dispenser    │
                                                                                       └──────────────┘
```

### 1️⃣ Chilli Plant Detection & Phenological Stage Estimation

- **Lead Researcher:** V.G.L. Sasmitha (IT23311640)
- **Core Technology:** YOLOv8 Object Detection, PyTorch, OpenCV, FastAPI
- **Key Capabilities:**
  - Real-time localization and bounding box detection of individual chilli plants (_Capsicum annuum L._) under changing outdoor illuminations.
  - Identification of phenological growth milestones (Seedling, Vegetative, Early Flowering, and Fruiting stages).
  - Target macronutrient baseline calculation according to the detected plant maturity stage.
  - Containerized with Docker for rapid portable field deployment (`docker compose` ready).

### 2️⃣ Soil Sensor vs. NPK Deficiency Comparator (NutrientOS)

- **Lead Researcher:** H.K.M. Kavishan (IT23312630)
- **Core Technology:** Electrochemical Probe Telemetry, Scientific Agronomy Engine, FastAPI
- **Key Capabilities:**
  - Ingestion of live soil electrochemical telemetry (Nitrogen, Phosphorus, Potassium, Soil pH, and Moisture).
  - Algorithmic cross-referencing between real-time subsurface sensor readings and stage-specific crop nutritional requirements.
  - Automated calculation of absolute nutrient deficits (mg/kg).
  - Formulates prescriptive micro-fertilizer recommendations (e.g., precise grams per square meter of Urea, Triple Superphosphate [TSP], and Muriate of Potash [MOP]).

### 3️⃣ Paddy Crop Gap Detection & Seed Dispenser Control (PaddyVision)

- **Lead Researcher:** Senanayake Y.M. (IT23284470)
- **Core Technology:** DeepLabV3+ with EfficientNet-B4 backbone, SegFormer-B0, COCO Segmentation, FastAPI
- **Key Capabilities:**
  - High-resolution multi-class semantic segmentation distinguishing between paddy seedlings (_Oryza sativa_), wet soil/mud, and invasive weeds.
  - Continuous canopy continuity tracking to detect gaps and discontinuities in planting rows.
  - Closed-loop integration with the physical seed dispensing mechanism to trigger localized seed release exactly over identified soil gaps.

### 4️⃣ Precise Pest Count & Multi-Class Infestation Quantifier (ChilliGuard Vision)

- **Lead Researcher:** G.A.T. Pesara (IT23275324)
- **Core Technology:** Custom-Trained High-Resolution YOLOv8, Scikit-learn, FastAPI
- **Key Capabilities:**
  - Microscopic insect body detection and individual headcount per leaf cluster.
  - Multi-class classification covering major destructive pests: **Aphids** (_Aphis gossypii_), **Chilli Thrips** (_Scirtothrips dorsalis_), **Caterpillars**, and **Whiteflies**.
  - Pest density quantification and biological risk scoring (Low, Moderate, High Infestation) to support targeted biopesticide spraying.

### 5️⃣ Autonomous Cable Robot Navigation & IoT Telemetry

- **Hardware & Firmware:** ESP32 Microcontroller, Stepper/Winch Motor Actuation, Load Cell Tension Sensors, Solar-Battery System.
- **Protocols:** MQTT Broker (Aedes), WebSockets, RESTful endpoints.
- **Capabilities:**
  - Smooth bi-directional suspension transit across long greenhouse or open-field cable tracks.
  - Real-time safety telemetry: winch cable tension monitoring, motor temperature, transit speed, and solar charge efficiency.
  - Manual override and automated scheduled patrol routines accessible via the web dashboard.

---

## 🛠️ Technology Stack

### **Frontend & Mission Control** 🖥️

- **Framework:** Next.js 16 (React 19, TypeScript)
- **Styling:** Tailwind CSS v4
- **Icons & UI:** Lucide React
- **Real-Time Communication:** MQTT.js, WebSocket Stream

### **AI Models & Backend Microservices** 🧠

- **API Framework:** FastAPI (Python 3.10–3.12, Uvicorn)
- **Deep Learning Frameworks:** PyTorch, Torchvision
- **Object Detection:** Ultralytics YOLOv8
- **Semantic Segmentation:** DeepLabV3+ (EfficientNet-B4), SegFormer-B0
- **Scientific Computing & Data Processing:** NumPy, Pandas, Scikit-learn, Albumentations, OpenCV

### **Robotics, Embedded & IoT** 🤖

- **Microcontroller:** ESP32 Dual-Core SoC
- **Communication Protocol:** MQTT (1883) & WebSockets
- **Embedded MQTT Broker:** Aedes (Node.js)
- **Actuators:** Winch motors, Cable tension management, Servo seed dispensing relays

### **DevOps & Tooling** ⚙️

- **Containerization:** Docker & Docker Compose
- **Automation Scripts:** Master Batch Launchers (`start_all_models.bat`, `stop_all_models.bat`)
- **Version Control:** Git & GitHub

---

## 🌐 Microservices & Port Allocation

| Service / Component                  | Port            | Endpoint / URL          | Interactive Swagger Docs     |
| ------------------------------------ | --------------- | ----------------------- | ---------------------------- |
| **Next.js Frontend Dashboard**       | `3000`          | `http://localhost:3000` | N/A                          |
| **Model 1: Chilli Plant Detection**  | `8000`          | `http://127.0.0.1:8000` | `http://127.0.0.1:8000/docs` |
| **Model 2: NPK Mix NutrientOS**      | `8501`          | `http://127.0.0.1:8501` | `http://127.0.0.1:8501/docs` |
| **Model 3: ChilliGuard Pest Vision** | `8002`          | `http://127.0.0.1:8002` | `http://127.0.0.1:8002/docs` |
| **Model 4: PaddyVision Seed Model**  | `8003`          | `http://127.0.0.1:8003` | `http://127.0.0.1:8003/docs` |
| **Aedes MQTT Broker (IoT)**          | `1883` / `8888` | `ws://localhost:8888`   | N/A                          |

---

## 🚀 Getting Started

### Prerequisites

- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS
- **Python:** 3.10, 3.11, or 3.12 (with CUDA support if running on GPU)
- **Node.js:** v20.x or higher & npm
- **Docker Desktop:** _(Optional, for containerized execution)_

---

### 1. Clone the Repository

```bash
git clone https://github.com/Lithira-Sasmitha/J26-IT-332-Intelligent-Autonomous-Robot-for-AI-Driven-Precision-Agriculture.git
cd J26-IT-332-Intelligent-Autonomous-Robot-for-AI-Driven-Precision-Agriculture
```

---

### 2. Launch All 4 AI Microservices (One-Click)

The repository includes pre-configured automation scripts that initialize all four FastAPI services in parallel:

```cmd
# Double click or run via Command Prompt:
start_all_models.bat
```

> **Note:** To terminate all running model servers cleanly, execute:

```cmd
stop_all_models.bat
```

#### Running Models Manually (Alternative)

<details>
<summary>Click to view manual service startup commands</summary>

- **Model 1 (Chilli Detection):**

  ```powershell
  cd Chilli_Plant_Detection_Model\Chilli_Plant_Detection_System\backend
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

- **Model 2 (NPK NutrientOS):**

  ```powershell
  cd NPK_Mix_Model
  .\run_backend.bat
  ```

- **Model 3 (ChilliGuard Pest Detection):**

  ```powershell
  cd pest-detection-model\ChilliGuard_Vision\ChilliGuard_Vision\backend
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
  ```

- **Model 4 (PaddyVision Segmentation):**
  ```powershell
  cd seed_dispensing_model
  .\run_backend.bat
  ```
  </details>

---

### 3. Launch Frontend Mission Dashboard

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open your browser and navigate to:

- **Mission Dashboard:** [http://localhost:3000](http://localhost:3000)
- **AI Analysis Center:** [http://localhost:3000/analysis](http://localhost:3000/analysis)
- **Cable Robot Navigation Control:** [http://localhost:3000/navigation](http://localhost:3000/navigation)
- **Seed Dispenser Real-Time Trigger:** [http://localhost:3000/dispenser](http://localhost:3000/dispenser)

---

### 4. Running Model 1 with Docker (Optional)

```bash
cd Chilli_Plant_Detection_Model\Chilli_Plant_Detection_System
docker compose up --build -d
```

Access Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📁 Repository Structure

```text
J26-IT-332-Intelligent-Autonomous-Robot-for-AI-Driven-Precision-Agriculture/
├── Chilli_Plant_Detection_Model/       # Model 1: Plant detection & phenology (YOLOv8)
│   └── Chilli_Plant_Detection_System/  # FastAPI backend & Docker configuration
├── NPK_Mix_Model/                      # Model 2: Soil sensor vs. deficiency comparator
│   ├── backend/                        # Agronomy calculation engine & FastAPI
│   └── run_backend.bat                 # Independent backend launcher
├── pest-detection-model/               # Model 3: Insect count & infestation quantifier
│   └── ChilliGuard_Vision/             # YOLOv8 weights, scripts, and FastAPI backend
├── seed_dispensing_model/              # Model 4: PaddyVision segmentation & gap seeding
│   ├── PaddyVision_Studio_Complete/    # DeepLabV3+ & SegFormer-B0 inference server
│   └── run_backend.bat                 # PaddyVision backend launcher
├── navigation_firmvare/                # ESP32 firmware & motor control code
├── frontend/                           # Next.js 16 Web Dashboard & MQTT clients
│   ├── src/app/                        # Next.js App Router routes (analysis, nav, etc.)
│   ├── src/components/                 # Telemetry, video feed & control UI components
│   └── scripts/mqtt-broker.js          # Built-in Aedes MQTT broker
├── start_all_models.bat                # Master batch script to launch all 4 models
├── stop_all_models.bat                 # Master batch script to terminate all models
└── README.md                           # Project documentation
```

---

## 📄 License

This research project is developed for academic purposes under the **SLIIT Faculty of Computing / Department of Information Technology**.

---

## 📞 Contact & Inquiries

For technical questions or collaboration regarding AgriBot, please reach out to the project team:

- **V.G.L. Sasmitha (IT23311640):** lithirasasmitha@gmail.com
- **H.K.M. Kavishan (IT23312630):** manjikavi8@gmail.com
- **Senanayake Y.M. (IT23284470):** yasirumadhusankasenanayake@gmail.com
- **G.A.T. Pesara (IT23275324):** thevindupesara@gmail.com

---

<div align="center">
  <p>🌱 <i>Advancing Sustainable Farming through Autonomous Robotics and Applied Artificial Intelligence</i> 🌱</p>
</div>
