# TerraDetective (NASA Space Apps Challenge 2026)
### *Earth System Trend Analysis & Regional Divergence Workbench*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React: 18](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Pytest: 25 Passed](https://img.shields.io/badge/Pytest-25%2F25%20Passing-10B981.svg)](https://docs.pytest.org)
[![Local AI: all-MiniLM-L6-v2](https://img.shields.io/badge/Dense%20Matcher-all--MiniLM--L6--v2-8B5CF6.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Local LLM: Ollama qwen3:8b](https://img.shields.io/badge/Local%20LLM-Ollama%20qwen3%3A8b-EC4899.svg)](https://ollama.ai)

---

## 🌍 Executive Summary

**TerraDetective** is an operational, full-stack Earth System workbench developed for the **NASA Space Apps Challenge 2026** ("*Be An Earth System Trend Detective!*"). 

While traditional climate portals plot individual satellite variables in isolation, TerraDetective acts as an automated Earth system detective. It combines **12-month Loess Seasonal Decomposition (STL)** and **Mann-Kendall rank trend analysis** across multi-decadal time series (2001–2025) with an **AI Variable Recommender** to uncover **counter-intuitive regional divergence paradoxes**—where surface greening masks acute groundwater depletion, or canopy loss induces localized micro-climatic thermal surges.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph DataPillars["The 4 Earth System Data Pillars (./data/)"]
        P1["Pillar 1: Catalog JSON<br/>NASA POWER 20-Variable Catalog"]
        P2["Pillar 2: Precipitation CSVs<br/>NASA Giovanni GPM IMERG Final v07"]
        P3["Pillar 3: Surface Thermal & Canopy<br/>NASA AppEEARS MODIS MOD11A2 & MOD13A3"]
        P4["Pillar 4: Hydrology Benchmark<br/>NASA GES DISC GLDAS Noah v2.1"]
    end

    subgraph BackendEngine["Backend Statistical & AI Engine (FastAPI)"]
        DL["Dynamic File Discovery & Parser<br/>(Dynamic skiprows & missing-flag sanitizer)"]
        SE["Stats Engine<br/>• 12-Month Loess STL Decomposition<br/>• Seasonal & Original Mann-Kendall<br/>• Sen's Median Slope / Decade (x120)"]
        AI["AI Detective & Recommender<br/>• Dense Matcher: sentence-transformers all-MiniLM-L6-v2 (384-d)<br/>• Local LLM Verdict: qwen3:8b via Ollama REST API<br/>• Resilient Deterministic Physical Synthesizer Fallback"]
        NC["NASA POWER Live API Client<br/>• Strips 'YYYY13' Annual Summary Keys<br/>• Physics-based MERRA-2 Climatology Fallback"]
        ED["NASA Earthdata Client<br/>• Bearer JWT Auth & CMR Metadata Search"]
    end

    subgraph FrontendUI["High-Density Scientific Workbench (React + Vite + Tailwind)"]
        CB["Top Command Bar<br/>• Natural-Language Detective Query<br/>• 4 One-Click Paradox Case Study Presets"]
        MAP["Dual-Region Split-Screen Comparator<br/>• Dual Interactive Leaflet Maps<br/>• Global Coordinate Inspector"]
        PLT["Interactive Plotly Timeseries<br/>• Raw Monthly Scatter + Bold STL Trend<br/>• 12-Mo Seasonality & Residual Toggles"]
        BG["Bento Grid Metrics Cards<br/>• Sen's Slope (Emerald p < 0.05 / Amber p >= 0.05)<br/>• Mann-Kendall p-value, Z-score, Tau<br/>• Total % Decadal Shift<br/>• AI Detective Briefing"]
        DRAWER["Methodology & Citations Drawer<br/>• NASA, CSA, SWOT & KNMI Attributions"]
    end

    DataPillars --> DL
    DL --> SE
    DL --> AI
    NC --> SE
    SE --> FrontendUI
    AI --> FrontendUI
```

---

## 🔬 Mathematical & Statistical Methodology

### 1. STL Seasonal Decomposition
To isolate multi-decadal anthropogenic and climatic signals from repeating astronomical phenology, raw observations $Y_t$ are decomposed into additive components using Loess smoothing with a strict 12-month period ($N_{period} = 12$):

$$Y_t = T_t + S_t + R_t$$

Where:
- $T_t$: **Deseasonalized Trend Component** (low-frequency secular climate trajectory).
- $S_t$: **12-Month Seasonal Cycle Component** (periodic phenological/orbital harmonic).
- $R_t$: **Residual Anomaly Component** (transient extreme weather events, ENSO shocks, volcanic noise).

### 2. Mann-Kendall Non-Parametric Trend Test
The monotonic trajectory of the series is evaluated without assuming normal Gaussian error distributions:

$$S = \sum_{k=1}^{n-1} \sum_{j=k+1}^n \text{sgn}(x_j - x_k)$$

$$\text{Var}(S) = \frac{n(n-1)(2n+5) - \sum_{p=1}^g t_p(t_p-1)(2t_p+5)}{18}$$

The standardized test statistic $Z$ follows a standard normal distribution, yielding the exact two-tailed $p$-value tested against the significance threshold $\alpha = 0.05$:

$$\text{is\_significant} = (p < 0.05)$$

### 3. Sen's Median Slope per Decade
The magnitude of the trend is computed using the median of all pairwise observation slopes. For monthly climate series, the median slope is scaled to the standardized 120-month decadal rate:

$$Q_{decade} = \text{median}\left( \frac{x_j - x_i}{j - i} \right) \times 120$$

---

## 🧪 The 4 Earth System Paradox Case Studies

TerraDetective includes 4 pre-configured, empirical paradox benchmarks validated using uploaded satellite data:

| # | Case Study | Region A vs. Region B | Opposing Data Pillars | Earth System Physical Mechanism |
|---|---|---|---|---|
| **1** | **Amazon Arc of Deforestation** | Rondonia Arc (`-10.88°, -61.93°`) vs. Intact Central Basin | AppEEARS MODIS `MOD11A2` (LST) vs. `MOD13A3` (NDVI) | **Bowen Ratio Collapse:** Loss of vegetative transpiration converts net radiation from latent heat cooling into severe sensible heat skin warming (+0.38°C/dec). |
| **2** | **Punjab Agricultural Greening Paradox** | Punjab Irrigated Belt (`30.90°, 75.86°`) vs. Upper Gangetic | AppEEARS MODIS `MOD13A3` (NDVI) vs. GES DISC `GLDAS` Noah | **Anthropogenic Groundwater Decoupling:** Tube-well irrigation produces strong positive surface greening (+0.028/dec), masking severe continuous root-zone soil water exhaustion (-5.04 kg/m²/dec). |
| **3** | **Indian Monsoon Divergence** | Central Semi-Arid Basin (`19.25°, 76.25°`) vs. Meghalaya Orographic Belt (`25.25°, 91.50°`) | Giovanni GPM IMERG `07_precipitation` | **Monsoon Trough Migration:** Increasing drought vulnerability and rainfall drying in central basins vs. convective rainfall intensification on orographic barriers. |
| **4** | **Sahelian Climate Dilemma** | Western Sahel (`14.50°, -1.50°`) vs. Sahara Margin (`18.00°, -1.00°`) | NASA POWER `T2M` vs. `PRECTOTCORR` & `GWETROOT` | **Thermal Hyper-Warming vs. Sporadic Pulses:** Decadal temperature surge (+0.35°C/dec) outpacing sporadic episodic precipitation greening events. |

---

## 📡 NASA & Partner Data Provenance

1. **NASA Giovanni (GES DISC):** GPM IMERG Final Run Monthly Precipitation (`GPM_3IMERGM_07_precipitation`), Area-Averaged Time Series.
2. **NASA AppEEARS:** Terra MODIS 8-Day 1km Land Surface Temperature (`MOD11A2.061`) & Monthly 1km Normalized Difference Vegetation Index (`MOD13A3.061`).
3. **NASA GES DISC GLDAS:** Global Land Data Assimilation System Noah Land Surface Model v2.1 0.25° Monthly Root Zone Soil Moisture (`RootMoist_inst`).
4. **NASA POWER Project:** NASA Langley Research Center MERRA-2 Climatology and CERES Radiation Assimilation (20-variable metadata catalog).
5. **International Benchmarks:** NASA SWOT (Surface Water and Ocean Topography), Canadian Space Agency (CSA RCM / Geo.ca), and Royal Netherlands Meteorological Institute (KNMI Climate Explorer).

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** v18, v20, or v22+ (npm 9+)

### 1. Workspace Configuration
Recommended workspace root:
```bash
# Recommended active workspace directory:
cd C:\Users\HP\.gemini\antigravity\scratch\terradetective
```

### 2. Backend Setup & Test Suite
```bash
# Install backend Python dependencies
python -m pip install -r backend/requirements.txt

# Run the complete automated test suite (25/25 passing)
python -m pytest backend/tests -v
```

### 3. Launching the Unified Full-Stack Workbench
TerraDetective is compiled into a single-port full-stack service:
```bash
# Start backend API and frontend workbench on port 8000
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend
```
Open your browser to:
👉 **`http://127.0.0.1:8000`**

### 4. Optional Frontend Development Mode
If you wish to modify the React / Tailwind UI with hot-module reloading:
```bash
cd frontend
npm run dev
```
Open your browser to:
👉 **`http://127.0.0.1:5173`** (proxies `/api` requests to `http://127.0.0.1:8000`).

---

## 🔒 Security & Code Quality Audit

- **OWASP Top 10 Compliant:** Strict Pydantic v2 input schemas enforcing geographic bounds ($-90 \le \text{lat} \le 90$, $-180 \le \text{lon} \le 180$).
- **Zero Hardcoded Secrets:** Authenticated live NASA API tokens and credentials are exclusively resolved via environmental parameters.
- **Dynamic Header Parsing:** Dynamic `skiprows` line detection safely parses arbitrary multi-line headers without file corruption.
- **Fail-Safe Offline Mode:** Physical MERRA-2 climatology fallback ensures uninterrupted workbench operation even during network interruptions.

---

## 📜 Submission Details

- **Event:** NASA International Space Apps Challenge 2026
- **Challenge:** *Be An Earth System Trend Detective!*
- **Team / Project:** TerraDetective
- **License:** MIT License
