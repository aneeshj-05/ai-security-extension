# AI Security Assistant

AI Security Assistant is a Chrome extension prototype backed by a local FastAPI
service. It provides real-time phishing URL analysis and fake-news content detection
using a combination of heuristic rules and trained Machine Learning (ML) models.

## Current Status

Implemented:

- Chrome extension popup UI.
- Active-tab URL lookup using the Chrome `tabs` API.
- Automatic page URL checks from the background service worker.
- Page-link scanning from a content script (with visual red outlines for suspicious links).
- Fake-news content scanning from a content script (with injected dismissible warning banners).
- Local FastAPI backend.
- `/health`, `/api/v1/analyze-url`, `/api/v1/analyze-urls-batch`, and `/api/v1/analyze-content` endpoints.
- Hybrid phishing detection (Heuristics + ML Random Forest).
- Hybrid fake-news detection (Heuristics + ML TF-IDF/PassiveAggressive).
- Automated dataset fetching (Tranco, OpenPhish, WELFake via Zenodo), preprocessing, and model training via a unified bash script.
- URL feature extraction and domain-age lookup through WHOIS.
- Typosquatting detection using fuzzy matching.

Not implemented yet:

- Trust-score API.
- Automated browser UI/integration tests.
- Production deployment setup.

## Project Structure

```txt
.
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   |-- fake_news.py
|   |   |   `-- phishing.py
|   |   |-- models/
|   |   |   `-- loader.py
|   |   |-- schemas/
|   |   |   |-- request.py
|   |   |   `-- response.py
|   |   |-- services/
|   |   |   |-- news_service.py
|   |   |   `-- phishing_service.py
|   |   |-- utils/
|   |   |   |-- text_processing.py
|   |   |   |-- url_features.py
|   |   |   `-- whois_lookup.py
|   |   `-- main.py
|   `-- run.py
|-- datasets/
|   |-- fake_news/
|   `-- phishing/
|-- extension/
|   |-- manifest.json
|   |-- background/
|   |   `-- background.js
|   |-- config/
|   |   `-- constants.js
|   |-- content/
|   |   `-- content.js
|   `-- popup/
|       |-- popup.html
|       |-- popup.css
|       `-- popup.js
|-- ml_models/
|   |-- fake_news/
|   |   |-- fetch_dataset.py
|   |   |-- preprocess.py
|   |   |-- train.py
|   |   `-- inference.py
|   `-- phishing/
|       |-- fetch_datasets.py
|       |-- train.py
|       `-- predict.py
|-- tests/
|-- run_ml_pipeline.sh
`-- requirements.txt
```

## How It Works

### 1. Backend Starts Locally
The backend is a FastAPI application defined in `backend/app/main.py`.
It exposes health checks and endpoints for analyzing single URLs, batches of URLs, and full page content.
The ML models (`model.pkl` files) are lazily loaded into memory when the server starts.

### 2. Chrome Extension Integrates
The `manifest.json` registers the popup, background worker, and content scripts.
- **Popup:** Retrieves active URL, sends it to the backend, and displays the risk score and verdict.
- **Background Worker:** Proxies API requests between content scripts and the FastAPI backend, and analyzes URLs automatically on tab updates.
- **Content Script:** 
  - Scans `<a>` tags and debounces requests to the backend. Outlines dangerous links in red.
  - Extracts the main article text (`document.body.innerText`) and sends it to the `/api/v1/analyze-content` endpoint. If classified as fake news, a red warning banner drops down from the top of the page.

### 3. Backend Analyzes
- **Phishing URLs:** Extracts lexical features (length, TLD, typosquatting) and WHOIS domain age. The rule engine calculates a base risk score. The ML model predicts a confidence score. If `ml_confidence >= 0.8` or `risk_score >= 30`, it flags the URL.
- **Fake News Content:** Extracts text features (sensational terms, clickbait titles, sentence length). The ML model predicts a confidence score. If `ml_confidence >= 0.75`, it is flagged as fake news.

## Setup

### Prerequisites

- Python 3.10 or newer.
- Google Chrome or another Chromium-based browser.

### 1. Install Dependencies & Train Models

This project includes a one-shot bash script that automatically sets up the Python environment, downloads the datasets (OpenPhish, Tranco, WELFake), preprocesses them, and trains the ML models.

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate
./run_ml_pipeline.sh
```

*(Note: The WELFake dataset is large, so downloading and training the TF-IDF vectorizer may take a few minutes).*

### 2. Configure Extension CORS

The backend does not allow all origins by default. After loading the unpacked extension in Chrome, copy its Chrome extension ID from `chrome://extensions` and export it:

```bash
export CHROME_EXTENSION_ID="your-extension-id"
```

Alternatively, provide explicit allowed origins:

```bash
export AI_SECURITY_ALLOWED_ORIGINS="chrome-extension://your-extension-id"
```

### 3. Run The Backend

Run the backend from inside the `backend/` folder:

```bash
cd backend
python run.py
```

Check the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

### 4. Load The Chrome Extension

1. Open Chrome and go to `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select the `extension/` folder from this project.
5. Visit any website (e.g., a news article) to see the extension actively scan links and content in the background!

## Testing The API Manually

### Phishing
```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze-url \
  -H "Content-Type: application/json" \
  -d '{"url":"https://paypal-secure-update.xyz"}'
```

### Fake News
```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze-content \
  -H "Content-Type: application/json" \
  -d '{"title": "BREAKING", "body_text": "This is a highly sensational and secret exposed article..."}'
```

## Running Backend Tests

Run tests from the project root:

```bash
source venv/bin/activate
PYTHONPATH=backend pytest tests/backend/
```

## Development Notes

- **ML Models:** The models are generated locally inside `ml_models/phishing/model.pkl` and `ml_models/fake_news/model.pkl`. They are ignored by Git.
- **Datasets:** Stored in `datasets/` and also ignored by Git.
- Keep backend code inside `backend/app/` and extension UI code inside `extension/`.
