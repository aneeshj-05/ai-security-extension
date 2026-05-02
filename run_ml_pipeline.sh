#!/usr/bin/env bash
# ── AI Security Extension — Full ML Pipeline Runner ───────────────────────────
# Usage: bash run_ml_pipeline.sh
# Run this from the project root directory.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Activate virtual environment if present ───────────────────────────────────
if [ -f "venv/bin/activate" ]; then
  echo "→ Activating virtual environment…"
  source venv/bin/activate
else
  echo "⚠  No venv found. Install deps with: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# ── Step 1: Install / refresh dependencies ────────────────────────────────────
echo ""
echo "━━━ [1/5] Installing dependencies ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip install -q -r requirements.txt

# ── Step 2: Fetch phishing dataset ───────────────────────────────────────────
echo ""
echo "━━━ [2/5] Fetching phishing dataset ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ml_models/phishing/fetch_datasets.py

# ── Step 3: Fetch & preprocess fake-news dataset ─────────────────────────────
echo ""
echo "━━━ [3/5] Fetching fake-news dataset ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ml_models/fake_news/fetch_dataset.py

echo ""
echo "━━━ [4a/5] Preprocessing fake-news dataset ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ml_models/fake_news/preprocess.py

# ── Step 4: Train models ──────────────────────────────────────────────────────
echo ""
echo "━━━ [4b/5] Training phishing model ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PYTHONPATH="$(pwd)/backend:$(pwd)" python ml_models/phishing/train.py

echo ""
echo "━━━ [4c/5] Training fake-news model ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python ml_models/fake_news/train.py

# ── Step 5: Verify model files ────────────────────────────────────────────────
echo ""
echo "━━━ [5/5] Verifying model files ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PHISHING_PKL="ml_models/phishing/model.pkl"
FAKE_NEWS_PKL="ml_models/fake_news/model.pkl"

check_model() {
  local path="$1"
  local label="$2"
  if [ -f "$path" ] && [ "$(stat -c%s "$path")" -gt 1000 ]; then
    echo "  ✓ $label — $(du -sh "$path" | cut -f1)"
  else
    echo "  ✗ $label — file missing or empty!"
    exit 1
  fi
}

check_model "$PHISHING_PKL" "Phishing model"
check_model "$FAKE_NEWS_PKL" "Fake-news model"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ ML pipeline complete."
echo "  Start the backend:  cd backend && python run.py"
echo "  Load the extension: open chrome://extensions → Load unpacked → extension/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
