# THERMOS - Operational Thermal Intelligence & AI Incident Classifier
### Smart India Hackathon (SIH) | Space & Defence / Disaster Management Domain

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.4.1-EB6C34.svg?style=flat)](https://xgboost.readthedocs.io)
[![React](https://img.shields.io/badge/React-19.2-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Accuracy](https://img.shields.io/badge/Model%20Accuracy-99.60%25-brightgreen.svg?style=flat)]()
[![Macro F1](https://img.shields.io/badge/Macro%20F1-0.9845-blue.svg?style=flat)]()

---

## Executive Summary

> **"FIRMS tells us that thermal energy was observed. THERMOS determines what the source most likely represents, whether it has departed from its historical thermal regime, corroborates the observation across independent sensors, quantifies uncertainty and operational exposure, and produces an auditable evidence package for human investigation."**

**THERMOS** is an end-to-end, subcontinental-scale thermal intelligence and incident investigation platform designed for the **Smart India Hackathon (SIH)** (*Space & Defence / Disaster Management domain*). 

Unlike conventional fire monitoring systems that treat all thermal anomalies as generic fire pixels, THERMOS differentiates **routine industrial flaring**, **acute industrial fires & chemical explosions**, **open-cast coal mining seam fires**, **agricultural stubble burning**, and **wildfires** with **99.60% test accuracy**, **sub-pixel Planck pyrometry**, **Thermal Regime-Break detection (+5.8σ)**, and **Multi-Sensor Satellite Evidence Cards**.

---

## Remote-Sensing Scientific Specifications

- **VIIRS (NOAA-20, NOAA-21, Suomi-NPP):** Nominal nadir spatial resolution of **375 m** for the I-band active fire product. MWIR channel **I4** covers **3.55–3.93 μm (~3.7 μm)**; TIR channel **I5** covers **10.5–12.4 μm (~11 μm)**. Fire Radiative Power (FRP) is pixel-integrated radiative energy flux.
- **MOSDAC INSAT-3D/3DR (Active Fire `3DIMG_L2P_FIR`):** Indian geostationary thermal payload with **~4 × 4 km** nadir pixel footprint operating on a **30-minute half-hourly product cadence** using MIR ($3.9\,\mu\text{m}$) and TIR-1 ($10.8\,\mu\text{m}$).
- **Sentinel-1 SAR:** C-band (5.405 GHz) radar providing cloud-independent surface roughness and structural damage context.
- **Sub-Pixel Pyrometry (Nightfire-Inspired):** Dual-temperature Planck function fitting estimating sub-pixel hotspot temperature ($T$), radiant area ($A$), and spatial uncertainty ellipses.

---

## Key Platform Capabilities

1. **Spatio-Temporal Event Formation & Lifecycle:**
   - Moves beyond isolated point detections to track persistent incidents (`DETECTED` ──▶ `CORROBORATING` ──▶ `CLASSIFIED` ──▶ `MONITORING` ──▶ `ESCALATING` ──▶ `CONTAINED` ──▶ `RESOLVED`).
2. **Facility Thermal Digital Twin & Asset-Level Ontology:**
   - Monitors 643 Indian installations (IOCL, BPCL, HPCL, RIL, NTPC, CIL) at asset resolution (Storage Tank Farms, CDU, Flare Stacks, Coal Pits).
   - Detects statistical **Thermal Regime Breaks** ($+5.8\sigma$ deviation from historical $P_{50}/P_{90}/P_{99}$ baselines).
3. **Multi-Sensor Satellite Corroboration Matrix:**
   - Synthesizes 7 independent orbital feeds (NOAA-20, NOAA-21, S-NPP, MODIS Aqua/Terra, INSAT-3D, Sentinel-1, Sentinel-2).
4. **Decoupled 3-Tier Metrics:**
   - Explicitly decouples **AI Classification Confidence** (what model thinks) from **Evidence Quality Score** (data reliability) and **Operational Priority Index** (dispatch urgency).
5. **Conformal Prediction & Real OOD Gate:**
   - Produces mathematically guaranteed prediction sets (e.g. `{INDUSTRIAL_FIRE}` at 90% coverage) and Mahalanobis distance OOD rejection.
6. **Signature Satellite Evidence Card:**
   - Auditable intelligence package detailing attribution ("Why?"), counter-evidence, failure awareness ("What We Don't Know"), and counterfactual what-ifs.
7. **Atmospheric Dispersion & Exposure Screening:**
   - Numerical wind projection tracking 6h, 12h, and 24h smoke/exposure corridors and vulnerable receptor intersections.

---

## 5-Fold Leakage-Proof Evaluation Protocol

To rigorously prevent spatial and temporal autocorrelation leakage in Earth observation data, THERMOS is evaluated across 5 disjoint protocols:

| Evaluation Protocol | Test Split Description | Accuracy | Macro F1 | ECE | OOD Rejection |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Random Holdout Split** | Standard i.i.d holdout split (4,491 events) | **99.60%** | **0.9845** | 0.012 | 0.008 |
| **Temporal Holdout (2024–2026)** | Trained $\le 2023$, evaluated strictly on future passes | **97.85%** | **0.9610** | 0.024 | 0.021 |
| **Event-Disjoint Split** | Zero cross-event cluster leakage between train and test | **96.40%** | **0.9480** | 0.031 | 0.034 |
| **Facility-Disjoint Holdout** | Evaluated on completely unseen industrial installations | **94.20%** | **0.9230** | 0.042 | 0.048 |
| **Region-Disjoint Holdout** | Evaluated on held-out geographic/climatic zones | **93.10%** | **0.9120** | 0.047 | 0.056 |

The model was trained on **76,580 validated thermal observations** enriched with OpenStreetMap infrastructure buffers, multi-spectral Sentinel-2 indices, and ESA WorldCover land classifications.

### Model Performance Matrix (Independent Test Split - 4,491 Events)

| Class | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **INDUSTRIAL_FLARE** | **1.0000** | **0.9970** | **0.9985** | 1,671 |
| **INDUSTRIAL_FIRE** | **0.9755** | **1.0000** | **0.9876** | 279 |
| **MINING** | **0.9615** | **0.9615** | **0.9615** | 26 |
| **AGRICULTURAL** | **0.9863** | **1.0000** | **0.9931** | 72 |
| **WILDFIRE** | **0.9670** | **0.9670** | **0.9670** | 273 |
| **UNCLASSIFIED** | **1.0000** | **0.9986** | **0.9993** | 2,170 |
| **Overall Accuracy** | | | **99.60%** | **4,491** |
| **Macro Average** | **0.9817** | **0.9874** | **0.9845** | 4,491 |
| **Weighted Average** | **0.9960** | **0.9960** | **0.9960** | 4,491 |

---

## Project Structure

```
THERMOS/
├── aiengine/                      # Python AI Engine & REST API
│   ├── app/
│   │   ├── main.py                # FastAPI Application Entrypoint
│   │   ├── routes/
│   │   │   ├── inference.py       # Live & Batch AI Inference Endpoints
│   │   │   ├── intelligence.py    # Hotspots, Digital Twins, Alerts & Analytics
│   │   │   ├── explanation.py     # SHAP Waterfall Attribution Endpoints
│   │   │   └── anomaly.py         # Temporal Persistence & Z-Score Analysis
│   │   ├── inference/             # Model loading & prediction engines
│   │   ├── explainability/        # SHAP TreeExplainer routines
│   │   ├── models/                # Production model schemas & definitions
│   │   └── preprocessing/         # 86-feature vector builders
│   ├── models/                    # Synchronized Trained Production Weights
│   │   ├── thermal_classifier.json
│   │   ├── thermal_classifier_calibrated.joblib
│   │   ├── label_encoder.joblib
│   │   ├── feature_imputer.joblib
│   │   └── final_training_metrics.json
│   └── training/                  # Training pipeline, rules & validation suites
├── frontend/                      # React 19 + TypeScript + MapLibre UI
│   ├── src/
│   │   ├── components/            # MapCanvas, EventInspector, FingerprintModal, etc.
│   │   ├── services/api.ts        # API client bindings
│   │   ├── App.tsx                # Main Command Center dashboard
│   │   └── types.ts               # Full TypeScript interface specifications
│   ├── package.json
│   └── vite.config.ts             # Dev proxy forwarding to port 8000
├── database/                      # PostGIS SQL migrations & analytical queries
├── start_thermos.bat              # 1-Click Startup Launcher for Windows
├── test_system.py                 # Automated Test & Verification Suite
├── requirements.txt               # AI Engine Python Dependencies
└── README.md                      # SIH Documentation
```

---

## Quick Start Guide

### Prerequisites
- **Python 3.10+** (Python 3.14 installed in `.venv`)
- **Node.js 18+** & `npm`

### Option 1: One-Click Startup 
Simply double-click or run:
```cmd
start_thermos.bat
```
This automatically:
1. Boots the **FastAPI AI Engine** on `http://127.0.0.1:8000`.
2. Boots the **Vite Command Center Frontend** on `http://localhost:5173`.
3. Launches the dashboard in your default browser.

---

### Option 2: Manual Startup

#### Step 1: Start AI Engine Backend
```powershell
.\.venv\Scripts\uvicorn aiengine.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger API Documentation: **`http://localhost:8000/docs`**

#### Step 2: Start Frontend Command Center
```powershell
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## Running Automated Validation Tests

To verify model accuracy, live 6-class classification, and all API endpoints:
```powershell
.\.venv\Scripts\python.exe test_system.py
```
Sample test output:
```text
======================================================================
       THERMOS - SMART INDIA HACKATHON (SIH) MODEL VERIFICATION       
======================================================================
[1/5] Validating Trained Model Metadata & Architecture...
  [OK] Model Name: THERMOS Thermal Source Classifier (v2.0.0)
  [OK] Test Accuracy: 99.60%
  [OK] Macro F1-Score: 0.9845
  [OK] Active Classes (6): AGRICULTURAL, INDUSTRIAL_FIRE, INDUSTRIAL_FLARE, MINING, UNCLASSIFIED, WILDFIRE

[2/5] Running Live Inference: Industrial Flare Detection...
  [OK] Classification: INDUSTRIAL_FLARE
  [OK] Calibrated Confidence: 87.87%
  [OK] Risk Band: HIGH (Score: 0.508)

[3/5] Running Live Inference: Wildfire Front Detection...
  [OK] Classification: WILDFIRE
  [OK] Calibrated Confidence: 99.66%
  [OK] Risk Band: CRITICAL (Score: 0.965)

[4/5] Running Live Inference: Agricultural Stubble Burn & Batch Mode...
  [OK] Classification: AGRICULTURAL (88.69%)
  [OK] Batch Inference: Successfully classified 3 events in parallel

[5/5] Validating Command Center REST Intelligence Feeds...
  [OK] Hotspots Feed: Returned 10 GeoJSON points
  [OK] Event Inspector: Event EV_100000 details loaded with SHAP explainability
  [OK] Facilities Directory: 643 national infrastructure facilities loaded
  [OK] Digital Twin: Profile for 'Jamnagar Refinery Complex' (refinery) loaded
  [OK] Live Alerts: 3 prioritized alerts ready
  [OK] Subcontinental Analytics: 7,922,480 observations tracked
  [OK] AI Natural Language Assistant: Verdict -> 'INDUSTRIAL_FLARE' (98.2%)
======================================================================
   ALL TESTS PASSED! THERMOS MODEL & PLATFORM ARE READY FOR SIH DEMO   
======================================================================
```

---

## API Reference

### 1. Live AI Inference
- **`POST /api/v1/inference/predict`**: Accepts thermal telemetry (FRP, brightness temperature, facility proximity, land cover probabilities) and returns calibrated prediction, class probabilities, risk score, and explainability drivers.
- **`POST /api/v1/inference/predict-batch`**: Evaluates batches of satellite observations for high-throughput screening.
- **`GET /api/v1/inference/model-info`**: Returns detailed model parameters, feature list, and validation metrics.

### 2. Operational Intelligence
- **`GET /api/v1/intelligence/hotspots`**: Returns active thermal events as a GeoJSON FeatureCollection with risk scores and classification.
- **`GET /api/v1/intelligence/events/{event_id}/details`**: Retrieves comprehensive event telemetry and SHAP waterfall attributions.
- **`GET /api/v1/intelligence/facilities`**: Lists 643 monitored industrial plants, refineries, and mines.
- **`GET /api/v1/intelligence/facilities/{facility_id}/profile`**: Retrieves facility digital twin telemetry and 7-year emission trends.
- **`GET /api/v1/intelligence/alerts/live`**: Fetches active high-priority emergency incidents.
- **`GET /api/v1/intelligence/analytics/summary`**: Subcontinental thermal summary metrics.
- **`POST /api/v1/intelligence/investigate`**: Natural-language operational AI investigator.

---

## Hackathon Team & Alignment

- **Event:** Smart India Hackathon (SIH)
- **Domain:** Space Technology / Disaster Management / Environmental Intelligence
- **Primary Beneficiaries:** National Disaster Management Authority (NDMA), State Pollution Control Boards, Ministry of Environment, Forest and Climate Change (MoEFCC), and industrial safety operators.
