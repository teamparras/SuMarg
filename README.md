<div align="center">

# 🚗 SuMarg: Smart Urban Mobility & Autonomous Routing Guidance
**Real-Time Autonomous Auto-Brake, Adaptive Cruise Control (ACC) & Traffic Optimization using Eclipse SUMO, Python TraCI, and Machine Learning**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Eclipse SUMO](https://img.shields.io/badge/Simulator-Eclipse%20SUMO%201.27%2B-1E88E5?style=for-the-badge)](https://eclipse.dev/sumo/)
[![Scikit-Learn](https://img.shields.io/badge/ML%20Engine-Scikit--Learn%20%7C%20LightGBM-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Control Loop](https://img.shields.io/badge/TraCI%20Loop-100ms%20(10Hz)-00C853?style=for-the-badge)](#)
[![Phase-1 Status](https://img.shields.io/badge/Phase--1%20MVP-100%25%20Completed-success?style=for-the-badge)](#)

</div>

---

## 📌 Project Overview

**SuMarg** is an **Edge-First Autonomous Driving & ADAS (Advanced Driver Assistance System) Digital Twin Platform** built over real-world Indian road networks using **OpenStreetMap (OSM)** and **Eclipse SUMO**. 

According to the **Ministry of Road Transport & Highways (MoRTH)** report, **71.2%** of road crashes in India are caused by over-speeding and late braking, while **21.2%** of all accidents are **"Hit from Back" (Rear-End Collisions)** due to slow human reaction times ($1.5\text{ to }2.2\text{ seconds}$). Additionally, **CSIR-CRRI** studies highlight that stop-and-go braking wastes **20%–35% extra fuel** at intersections.

**SuMarg solves this by replacing the $2\text{-second}$ human reaction delay with a $100\text{ms}$ ($0.1\text{s}$) Python TraCI + Machine Learning Regression loop** that reads real-time front radar telemetry and executes smooth, collision-free deceleration in less than $1\text{ millisecond}$.

---

## ✨ Key Autonomous Functionalities (Phase-1 MVP)

### 1. 🛑 Autonomous Emergency Auto-Braking (AEB)
* Overrides SUMO's built-in Krauss safety driver (`SpeedMode = 0`) so that vehicle stopping is governed **100% by our trained Machine Learning model (`model.pkl`)**.
* Continuously monitors bumper-to-bumper `leader_distance` (via a $100\text{m}$ front radar) and computes real-time **Time-to-Collision ($\text{TTC}$)**.
* When a critical hazard or sudden cut-in is detected ($\text{TTC} \le 1.2\text{s}$ or $\text{gap} \le 6.0\text{m}$), the actuator triggers an instant $9.0\text{ m/s}^2$ emergency full stop (`0.0 m/s`), halting safely behind stationary obstacles with **Zero Collision**.

### 2. 🟠 Smooth Adaptive Cruise Control (ACC / Auto-Slowdown)
* Unlike discrete classification models that cause jerky speed jumps, SuMarg uses a **Supervised Regression Pipeline** (`preprocessor.pkl` + `model.pkl`) to predict exact continuous decimal velocities ($0.0\text{ to }22.0\text{ m/s}$).
* Automatically matches the velocity of slower leading vehicles while maintaining a dynamic **$1.5\text{-second}$ safe time headway** using smoothed TraCI actuation (`traci.vehicle.slowDown()`).

### 3. 🎨 Real-Time 3-State Visual Feedback (`LongitudinalController`)
To provide transparent, explainable AI verification during live `SUMO-GUI` demonstrations, the Ego Vehicle dynamically changes its body color based on the active ML decision state:

| Visual State | Vehicle Color in SUMO-GUI | Trigger Condition | Autonomous Action Executed |
| :--- | :--- | :--- | :--- |
| **State 1: Cruise** | 🔵 **BLUE** `(0, 100, 255)` | Clear road ahead ($\text{gap} > 45\text{m}$) | Smoothly accelerates up to the lane `speed_limit`. |
| **State 2: Auto-Slow** | 🟠 **ORANGE** `(255, 165, 0)` | `target_speed < current_speed - 0.8` | Gradual ACC deceleration over $0.5\text{s}$ to match leader speed. |
| **State 3: Full Brake** | 🔴 **RED** `(255, 0, 0)` | `target_speed <= 0.5 m/s` or $\text{gap} \le 6\text{m}$ | Rapid emergency braking ($9.0\text{ m/s}^2$) over $0.2\text{s}$ to full stop. |

### 4. 🎯 Automated Camera Lock & "Sudden Leader Stop" Stress Test
* Automatically scans active traffic in `runner.py`, selects an Ego Car trailing a Leader Car, locks and zooms the `SUMO-GUI` camera onto the Ego Car, and highlights the Leader Car in **Yellow**.
* Includes a built-in **Live Stress Test** that forces the Yellow Leader Car to slam its brakes (`Speed = 0 m/s`) mid-road to visually prove real-time ML collision avoidance.

---

## 🏗️ System Architecture

```text
+-----------------------------------------------------------------------------------+
|                        1. SUMO DIGITAL TWIN (100ms Tick)                          |
|     Real-World OSM Network (osm.net.xml.gz) + Multi-Vehicle Traffic Simulation    |
+-----------------------------------------+-----------------------------------------+
                                          | Raw Telemetry via TraCI (Every 0.1s)
                                          v
+-----------------------------------------------------------------------------------+
|                     2. SENSOR EXTRACTION LAYER (traci_core)                       |
|  • getSpeed() -> vehicle_speed          • getLeader(100m) -> leader_distance      |
|  • getMaxSpeed() -> speed_limit         • Computed -> relative_speed & TTC        |
+-----------------------------------------+-----------------------------------------+
                                          | 6-Feature Input Vector (X)
                                          v
+-----------------------------------------------------------------------------------+
|                        3. ML DECISION ENGINE (ml_engine)                          |
|  • Feature Scaling : artifacts/preprocessor.pkl (StandardScaler Pipeline)         |
|  • Inference Model : artifacts/model.pkl (RandomForest / LightGBM Regressor)      |
|  • Output Label (Y): Continuous Safe Target Speed (0.0 m/s to 22.0 m/s)           |
+-----------------------------------------+-----------------------------------------+
                                          | Predicted Target Speed (m/s)
                                          v
+-----------------------------------------------------------------------------------+
|              4. LONGITUDINAL ACTUATION CONTROLLER (longitudinal_controller.py)    |
|  • 🔵 BLUE (Cruise)   |  🟠 ORANGE (Smooth ACC Decel)  |  🔴 RED (Emergency Stop) |
+-----------------------------------------------------------------------------------+
```

---

## 📊 Dataset Schema (7-Column Hybrid Physics & SUMO Telemetry)

To overcome the limitation that default SUMO vehicles rarely tailgate closely, our dataset (`braking_data.csv`) combines live SUMO traffic telemetry with **5,000+ synthetic emergency braking edge-cases**:

| Column Name | Role | Unit | TraCI / Physics Formula | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`vehicle_speed`** | Input ($X_1$) | $\text{m/s}$ | `traci.vehicle.getSpeed(ego_id)` | Current velocity and momentum of our Ego Vehicle. |
| **`leader_speed`** | Input ($X_2$) | $\text{m/s}$ | `traci.vehicle.getSpeed(leader_id)` | Velocity of the vehicle directly ahead. |
| **`leader_distance`** | Input ($X_3$) | $\text{m}$ | `traci.vehicle.getLeader(ego_id, 100)` | Bumper-to-bumper front radar gap. |
| **`relative_speed`** | Input ($X_4$) | $\text{m/s}$ | $v_{\text{ego}} - v_{\text{leader}}$ | Closing speed toward the leading vehicle. |
| **`time_to_collision`** | Input ($X_5$) | $\text{s}$ | $\frac{\text{leader\_distance}}{\text{relative\_speed}}$ | Seconds remaining before impact (clamped at $99\text{s}$ when safe). |
| **`speed_limit`** | Input ($X_6$) | $\text{m/s}$ | `traci.lane.getMaxSpeed(lane_id)` | Maximum legal speed allowed on the current lane. |
| **`target_speed`** | **Target ($Y$)** | $\text{m/s}$ | Continuous Regression Output | **Safe target velocity** for the next $0.1\text{s}$ step. |

---

## 📂 Project Directory Structure

```text
SuMarg/
├── ml_engine/
│   ├── artifacts/
│   │   ├── model.pkl                  # Trained Regression Model
│   │   ├── preprocessor.pkl           # Fitted StandardScaler Pipeline
│   │   ├── metrics.json               # Model R2 & MAE evaluation metrics
│   │   └── status.txt                 # Pipeline validation status
│   ├── config/
│   │   └── schema.yaml                # Strict 7-column dataset schema definition
│   ├── data/
│   │   ├── raw/braking_data.csv       # 5,000+ rows hybrid braking dataset
│   │   └── processed/                 # Automated train.csv & test.csv splits
│   └── src/                           # Modular MLOps training & transformation scripts
├── simulation/
│   ├── osm.sumocfg                    # Master SUMO simulation configuration
│   ├── osm.net.xml.gz                 # OpenStreetMap road network
│   ├── osm.passenger.trips.xml        # Multi-vehicle urban traffic trips
│   ├── osm.poly.xml.gz                # 3D/2D building & park polygons
│   └── osm.view.xml                   # SUMO-GUI camera & visual settings
├── traci_core/
│   ├── collectors/                    # Live telemetry & radar extraction scripts
│   ├── controllers/
│   │   └── longitudinal_controller.py # 3-State (Blue/Orange/Red) Auto-Brake actuator
│   ├── config.py                      # Centralized Pathlib & hyperparameter resolver
│   └── runner.py                      # Main 100ms real-time TraCI execution loop
├── verify_ml.py                       # Offline 4-scenario physics sanity test script
├── requirements.txt                   # Python dependencies
├── setup.py                           # Editable package installer
└── README.md                          # Project documentation
```

---

## 🚀 Getting Started & Installation

### 1. Prerequisites
* **Python 3.9+** installed on your system.
* **Eclipse SUMO (v1.20+)** installed and `SUMO_HOME` added to your system environment variables.

### 2. Install Dependencies
Clone the repository and install the required Python packages inside your virtual environment:

```bash
pip install -r requirements.txt
pip install -e .
```

---

## 🧪 How to Test & Run the Auto-Brake System

### Step 1: Run Offline ML Sanity Verification (No GUI Needed)
Verify that `preprocessor.pkl` and `model.pkl` accurately predict safe speeds across 4 extreme physics scenarios (Emergency Stop at $3.5\text{m}$, Slow Truck at $16\text{m}$, Steady Follow at $35\text{m}$, and Open Highway at $100\text{m}$):

```bash
python verify_ml.py
```

**Expected Output:**
* 🚨 **Emergency Cut-In ($\text{Gap} = 3.5\text{m}, \text{TTC} = 0.19\text{s}$):** Predicts `~0.00 m/s` (Full Brake)
* 🟠 **Slow Truck Ahead ($\text{Gap} = 16.0\text{m}, \text{TTC} = 1.23\text{s}$):** Predicts `~5.40 m/s` (Smooth Deceleration)
* 🔵 **Open Highway ($\text{Gap} = 100.0\text{m}, \text{Clear Road}$):** Predicts `~17.00+ m/s` (Cruising Acceleration)

### Step 2: Launch Live SUMO-GUI Auto-Brake Demonstration
Start the real-time $100\text{ms}$ closed-loop simulation in `SUMO-GUI`:

```bash
python traci_core/runner.py
```

**What You Will See in SUMO-GUI:**
1. The camera automatically locks onto our **ML Ego Car** following a **Yellow Leader Car**.
2. After $4\text{ seconds}$, the Yellow Leader Car slams its brakes (`Speed = 0.0 m/s`).
3. Watch the Ego Car transition from **🔵 Blue (Cruise) $\rightarrow$ 🟠 Orange (Auto-Slowdown) $\rightarrow$ 🔴 Red (Emergency Stop)** and halt safely **$\sim 6.0\text{ meters}$ behind the leader without colliding!**

---

## 🛣️ Roadmap (Phase-2 Upcoming Milestones)

- [x] **Phase-1:** Real-World OSM Digital Twin + Hybrid Dataset + Longitudinal ML Auto-Brake & ACC.
- [ ] **Phase-2 (Milestone 1):** **360° Blind-Spot Radar & Smart Overtaking** using `traci.vehicle.getNeighbors()` and a Random Forest Classifier.
- [ ] **Phase-2 (Milestone 2):** **GLOSA (Green Light Optimal Speed Advisory)** using `getNextTLS()` to glide through green traffic waves and save $20\%–35\%$ fuel.
- [ ] **Phase-2 (Milestone 3):** **Emergency Ambulance Green Corridor** (Auto-Yielding to the side lane).
- [ ] **Phase-2 (Milestone 4):** **20Hz FastAPI WebSocket + React.js Cockpit Dashboard** for live telemetry visualization.

---

## 👥 Team PARRAS & Credits

* **Project Title:** SuMarg — Smart Urban Mobility & Autonomous Routing Guidance
* **Developed By:** Team PARRAS (Department of Computer Science & Engineering)
* **License:** Academic & Research Use
