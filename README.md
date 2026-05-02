# 🔐 AI Security Browser Extension

## 📌 Overview

This project is a **browser extension (Chrome/Edge)** that acts as a real-time **AI-powered security assistant**. It helps users identify **phishing websites** and **fake or misleading content** while browsing.

The system analyzes a website’s URL and on-page text, assigns a **trust score**, and provides **clear explanations** for why something may be unsafe.

---

## 🚀 Key Features

* 🔍 **Real-time phishing detection**
* 📰 **Fake news detection from webpage content or selected text**
* 🧠 **Hybrid analysis (rule-based + ML-ready features)**
* 📊 **Trust score generation**
* 💡 **Explainable results (reasons for detection)**
* 🌐 **Domain intelligence (WHOIS-based age detection)**
* ✂️ **Text selection analysis (right-click to verify content)**

---

## ⚙️ How It Works

1. The browser extension captures the current website URL and/or selected text
2. Data is sent to the backend API
3. The backend performs:

   * **URL analysis** (phishing detection using features like entropy, typosquatting, domain age)
   * **Content analysis** (fake news detection using NLP models)
4. A combined evaluation produces:

   * Phishing verdict / content credibility
   * Trust score
   * Explanation (reasons)
5. Results are displayed directly in the browser

---

## 🏗️ Tech Stack

* **Backend:** FastAPI (Python)
* **Phishing Detection:** Rule-based + feature engineering (ML-ready)
* **Fake News Detection:** NLP (TF-IDF / ML models)
* **Frontend:** Chrome Extension (JavaScript)
* **Libraries:** thefuzz, python-whois, scikit-learn, Pydantic

---

## 📁 Project Structure

```id="n2j2qz"
backend/
  app/
    api/
    services/
    utils/
    schemas/
    main.py
extension/
  manifest.json
  popup.js
  content.js
```

---

## 🎯 Goal

To build a **real-time, explainable, and user-friendly security tool** that enhances browsing safety by combining **cybersecurity, machine learning, and NLP techniques**.

---

## 📌 Status

* ✔️ Backend phishing detection engine completed
* ✔️ Feature extraction and rule-based scoring implemented
* 🔄 Fake news detection integration in progress
* 🔄 Extension integration in progress

---
