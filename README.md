# Crypto Market Intelligence & Pattern Analysis System (Django)

An advanced **AI-inspired crypto analysis platform** built with Django that helps traders:
- Detect recurring market patterns in new coins
- Analyze token fundamentals + on-chain behavior
- Measure BTC correlation across timeframes
- Visualize market structure using interactive charts

This project combines **quant logic + behavioral market analysis + data visualization** into a single intelligent trading toolkit.

---

##  Key Features

### New Coin Pattern Intelligence Engine
A rule-based classification system that identifies **12+ recurring crypto market behaviors**, such as:

- Pump → Dump → Accumulation cycles
- VC / insider unlock dumps
- Slow bleed low-demand assets
- Institutional accumulation phases
- Fake pump & rug patterns
- Narrative rotation surges
- Futures-driven liquidations
- Liquidity trap reversals

Each pattern includes:
- Market structure classification
- Indicator-based scoring system
- Actionable trading advice
- Probabilistic next-move prediction

---

### Smart Coin Analyzer
A structured input engine that evaluates:

#### Fundamentals
- FDV (Fully Diluted Valuation)
- Team strength score
- Utility score
- Audit status
- Vesting pressure

#### On-Chain Behavior
- Whale inflows
- Holder concentration
- Liquidity depth
- Developer sell pressure
- Bot transaction activity

#### Technical Conditions
- RSI levels
- Initial price action (pump/dump/sideways)
- Funding rate signals
- Market structure bias

#### Sentiment Layer
- Social hype level
- Mentions multiplier
- Macro bullish sentiment
- Narrative strength

Outputs:
- Detected market pattern
- Trading advice
- Expected next move
- Confidence-adjusted signal strength

---

### BTC Correlation Visualizer
A professional-grade correlation analysis tool using **CCXT + Pandas + Plotly**

#### Features:
- BTC vs Altcoin correlation tracking
- Multiple trading styles:
  - Scalper (1H)
  - Day Trader (4H)
  - Swing Trader (1D)
  - Positional (1W)

#### Visual Outputs:
- Rolling correlation chart
- Normalized price comparison
- Gauge indicator for current correlation strength

#### Core Metrics:
- Rolling correlation coefficient
- Price return alignment
- Market dependency detection

---

### Interactive Market Tools
Additional utilities for crypto research:

- New coin checklist guide
- Pattern breakdown explorer
- Strategy documentation pages
- Structured coin analysis workflow

---

## Tech Stack

- **Backend:** Django (Python)
- **Data Engine:** Pandas, NumPy
- **Market Data API:** CCXT (Binance)
- **Visualization:** Plotly (interactive charts)
- **Frontend:** Django Templates (HTML/CSS)
- **Charts:** Plotly subplots + gauge indicators

---

## System Design Philosophy

This project is built on one core idea:

> “Crypto markets are not random — they are repeating behavioral patterns driven by liquidity, sentiment, and structure.”

Instead of relying on indicators alone, this system blends:
- Market microstructure
- Behavioral finance
- On-chain heuristics
- Statistical correlation analysis

---

## Project Structure


trading/
│
├── views.py # Core logic (patterns, analyzer, correlation)
├── patterns (list) # Market behavior classification engine
├── templates/
│ ├── index.html
│ ├── new_coin_analyzer.html
│ ├── new_coin_patterns.html
│ ├── new_coin_analysis.html
│ ├── new_coin_strategy.html
│ └── correlation_visualizer.html


---

## Pattern Engine (Core Logic)

The system classifies coins into patterns like:

- **Slow Bleed / Low Demand**
- **Pump → Dump → Accumulation**
- **Liquidity Trap (V-shape recovery)**
- **Institutional Accumulation**
- **Rug / Fake Pump Behavior**
- **Narrative Rotation Pumps**

Each pattern is derived using weighted signals from:
- Fundamentals (40%)
- On-chain data (30%)
- Technical indicators (20%)
- Market sentiment (10%)

---

## Correlation Engine (How it works)

1. Fetches OHLCV data from Binance via CCXT
2. Aligns BTC + selected coin time series
3. Computes:
   - Percentage returns
   - Rolling correlation (window-based)
4. Visualizes:
   - Correlation strength over time
   - Price normalization comparison

---

## Key Insights This Project Provides

- Whether a coin is **BTC-dependent or independent**
- Whether a coin is in **accumulation or distribution phase**
- Whether hype is **organic or bot-driven**
- Whether market structure is **healthy or manipulated**
- Whether a setup is **high probability or noise**

---

## Future Enhancements

- AI-based pattern classifier (ML model upgrade)
- Real-time WebSocket price streaming
- Backtesting engine for detected patterns
- Wallet tracking for whale detection
- Signal alert system (Telegram/Discord)
- TradingView integration for overlays

---

## Setup Instructions

```bash
git clone https://github.com/your-username/crypto-intelligence-system.git
cd crypto-intelligence-system

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

python manage.py migrate
python manage.py runserver
