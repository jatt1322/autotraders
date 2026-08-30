# Installation Guide

This INSTALL page explains how to install and run Autotraders locally and includes sample screenshots showing the UI and logs. Replace the sample images in /images with your real screenshots produced after running the app.

Prerequisites
- Python 3.8–3.11
- Git
- Internet for yfinance data

Quick install (copy/paste)

1. Clone the repository

```bash
git clone https://github.com/jatt1322/autotraders.git
cd autotraders
```

2. Create and activate a virtual environment

macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Upgrade pip and install core dependencies

```bash
pip install --upgrade pip setuptools wheel
# Install PyTorch (CPU-only example)
pip install torch --index-url https://download.pytorch.org/whl/cpu
# Install project requirements
pip install -r requirements.txt
# (Optional) install Streamlit for the UI
pip install -r requirements-additional.txt
```

4. Train a small test model (creates models/test_model.zip)

```bash
python train.py --ticker AAPL --start 2019-01-01 --end 2019-06-01 --timesteps 2000 --out models/test_model.zip
```

5. Run the simulation to generate trades and test online fine-tune

```bash
python run_loop.py --model models/test_model.zip --ticker AAPL --start 2019-07-01 --end 2019-08-01 --deposit 2000 --fine_tune_every 50 --fine_tune_steps 200
```

6. Start the Streamlit UI to view every logged trade

```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

Where the screenshots come from
- The screenshots in /images are placeholder SVGs demonstrating how the UI looks and where to expect logs and NAV plots.
- To capture your real screenshots:
  1. Run the simulator to produce logs/trades.csv (step 5).
  2. Start the Streamlit app (step 6).
  3. Use your OS/browser screenshot tool to capture the UI, save as PNG, and replace the sample images in /images (see notes below).

Replace the sample screenshots with real ones
- Save real screenshots as PNG (e.g., screenshot_ui.png, screenshot_trades.png, screenshot_logs.png).
- Replace or add files in the images/ directory and commit them:

```bash
# copy your screenshots into repo
cp ~/Downloads/screenshot_ui.png ./images/screenshot_ui.png
git add images/screenshot_ui.png
git commit -m "Add real UI screenshot"
git push origin main
```

Notes
- The sample images are SVG mockups and will display in the GitHub repository web view.
- If you replace them with PNGs, GitHub will also render PNGs on the repo page.
- If you want me to add your real screenshots for you, upload the PNGs here (or tell me where they are), and I can add them to the repo.

Troubleshooting
- If streamlit is not found, ensure your venv is active and you installed the additional requirements.
- If yfinance returns empty data: check ticker/date range and network access.
- If the UI shows no trades: verify logs/trades.csv exists and contains a timestamp and nav column.

