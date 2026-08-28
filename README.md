# CoinIntel - Crypto Trading Journal & Market Intelligence System

An intelligent, multi-user **Crypto Trading Journal & Market Analysis Platform** built with **Django**, **CCXT**, **Pandas**, and **Plotly**.

CoinIntel combines personal trade logging, emotional psychology auditing, pattern win-rate matrixes, and live exchange data (BTC correlation & new coin evaluation) into a clean, modern web application.

---

## 🌟 Key Features

### 🔐 1. Multi-User Authentication & Security
- **Email & Username Registration**: Account signup requiring validated email addresses.
- **Dual Sign In**: Log in using either registered **Username** or **Email Address**.
- **Forgot Password Workflow**: Complete 4-step password reset workflow (`/password-reset/`).
- **Account & Risk Preferences**: Configure account starting capital ($), max risk per trade (%), account tier badges, and custom avatars.
- **Multi-Tenant Data Isolation**: Every trader's trade entries, retrospective notes, and metrics are strictly private and isolated.

---

### 📓 2. Personal Trade Journal Engine
- **Automated Trade Metrics**: Auto-calculates Realized PnL ($), ROI (%), and executed vs planned Risk:Reward (**R-Multiple**) for Long and Short positions.
- **Advanced Trade Log Management**: Search and filter trade entries by symbol, status (*Win, Loss, Open, Breakeven*), or mindset state.
- **Detailed Trade Reports**: Deep-dive into trade parameters, entry/exit prices, stop loss targets, retrospective notes, and chart screenshot embeds.
- **Shareable Trade Cards**: Generate clean summary cards for Twitter/X, Discord, or Telegram sharing.
- **One-Click Demo Data Generator**: Instantly populate realistic sample trade entries on new accounts for immediate analytics exploration.

---

### 🧠 3. Trading Psychology & Mindset Audit
- **Emotional Mistake Audit**: Quantifies exact dollar losses tied to emotional trading habits (*FOMO, Revenge Trading, Over-leveraging, Panic Cuts*).
- **Disciplined Execution Rate**: Calculates your percentage of plan-compliant trade executions.
- **Emotional Tilt Warning Banner**: Detects consecutive emotional losses and suggests a mandatory cooldown break away from the screens.

---

### 💡 4. Strategy Patterns & Pre-Trade Setup Evaluator
- **12-Pattern Win-Rate Matrix**: Maps your logged trades against 12 recurring crypto market behaviors (Liquidity Traps, VC Dumps, Accumulation breakouts) to reveal your personal win-rate and expectancy per setup.
- **Pre-Trade Setup Evaluator**: Input coin metrics (FDV, Team score, Utility, RSI, Whale inflows, Audit status) to get an AI Setup Grade (**A+ to F**), win probability %, and safe max position risk BEFORE placing real capital.

---

### 📊 5. Quantitative Performance Analytics
- **Equity Growth Curve**: Interactive Plotly time-series chart showing account balance growth over time.
- **Win/Loss Ratio Distribution**: Donut charts and execution summary metrics.

---

### 📈 6. Live Crypto Market Tools
- **BTC Correlation Tool**: Fetches live Binance OHLCV data via CCXT, computing rolling correlation gauge indicators, correlation trend charts, and normalized price path comparisons across Scalper (1H), Day (4H), Swing (1D), and Positional (1W) timeframes.
- **Smart Coin Evaluator**: Evaluates new listed coin fundamentals, on-chain whale activity, and dump risk.
- **Guides & Checklists**: Reference documentation for 12 Market Patterns, New Coin Launch Checklist, and Strategy Manual.

---

## 🛠️ Tech Stack

- **Backend Framework:** Python 3.12+, Django 5
- **Market Data API:** CCXT (Binance live OHLCV data)
- **Data Engine:** Pandas, NumPy
- **Interactive Visualizations:** Plotly (Subplots, Gauges, Equity Curves)
- **Frontend UI:** HTML5, CSS3, Bootstrap 5, Bootstrap Icons, Inter Typography
- **Database:** SQLite3 (development / production configurable)

---

## 📂 Project Structure

```text
CoinIntel/
│
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── NewCoinSetup/               # Django Project Configuration
│   ├── settings.py             # App settings, DB, static files, Email backend
│   ├── urls.py                 # Main URL router
│   ├── wsgi.py                 # WSGI application entrypoint
│   └── asgi.py                 # ASGI application entrypoint
│
├── NewCoinSetupApp/            # Main Application App
│   ├── models.py               # UserProfile, TradeEntry, TradeChecklist models
│   ├── views.py                # Journal CRUD, Psychology Audit, Pattern Matrix, CCXT Correlation
│   ├── forms.py                # CustomUserCreationForm, EmailOrUsernameAuthenticationForm
│   ├── urls.py                 # App URL patterns & password reset routes
│   ├── tests.py                # Automated unit test suite (6 passing tests)
│   └── admin.py                # Django Admin registration
│
├── templates/                  # HTML Templates
│   ├── base.html               # Clean, single-line responsive navbar & footer
│   ├── index.html              # Landing page featuring upfront BTC Correlation & Coin Evaluator
│   ├── registration/           # Auth templates (login, signup, profile, password reset flow)
│   └── journal/                # Journal templates (dashboard, trade_list, trade_form, trade_detail, fomo_shield, pattern_edge, analytics)
│
└── static/                     # Static Assets
    ├── css/
    ├── js/
    └── img/
        └── favicon.svg         # SVG Favicon matching brand logo
```

---

## ⚙️ Setup & Installation Instructions

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/CoinIntel.git
cd CoinIntel

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Run Automated Unit Tests
```bash
python manage.py test
```

### 5. Launch Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
