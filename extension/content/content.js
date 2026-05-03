const SCAN_LIMIT = globalThis.AI_SECURITY_CONFIG.LINK_SCAN_LIMIT;
const WARNING_CLASS = "ai-security-suspicious-link";
const SAFE_CLASS = "ai-security-safe-link";
const FAKE_NEWS_BANNER_ID = "ai-security-fake-news-banner";
const FAKE_NEWS_HIGHLIGHT_CLASS = "ai-security-fake-news-highlight";
const FAKE_NEWS_LABEL_CLASS = "ai-security-fake-news-label";
const MIN_ARTICLE_WORDS = 20;

// Selectors for individual news cards/article items on listing pages
const CARD_SELECTORS = [
  "article",
  ".post",
  ".card",
  ".news-card",
  ".article-card",
  ".story-card",
  ".feed-item",
  ".entry",
  ".item",
  "[class*='article']",
  "[class*='story']",
  "[class*='post']",
  "[class*='card']",
];

// Selectors for a single full article page
const ARTICLE_SELECTORS = [
  "article",
  "[role='main']",
  "main",
  ".post-content",
  ".article-content",
  ".article-body",
  ".entry-content",
  ".story-body",
  ".news-content",
  ".content-body",
  ".post-body",
  ".td-post-content",
  "#article-body",
  "#main-content",
  "#content",
];

// ── Styles ────────────────────────────────────────────────────────────────────
function injectStyles() {
  if (document.getElementById("ai-security-link-styles")) {
    return;
  }

  const style = document.createElement("style");
  style.id = "ai-security-link-styles";
  style.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

    .${WARNING_CLASS} {
      outline: 1.5px solid #ff3c5a !important;
      outline-offset: 2px !important;
      background-color: rgba(255, 60, 90, 0.10) !important;
      border-radius: 3px !important;
    }

    .${WARNING_CLASS}::after {
      content: " ⚠ threat";
      color: #ff3c5a;
      font-family: 'Share Tech Mono', monospace;
      font-size: 10px;
      font-weight: 400;
      letter-spacing: 0.06em;
      margin-left: 5px;
    }

    /* ── Fake News Banner ── */
    #${FAKE_NEWS_BANNER_ID} {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 2147483647;
      background: #0a0e1a;
      color: #c9d8ef;
      font-family: 'Rajdhani', sans-serif;
      font-size: 14px;
      font-weight: 600;
      padding: 0 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      height: 44px;
      border-bottom: 1px solid #ff3c5a;
      box-shadow: 0 0 24px rgba(255, 60, 90, 0.25), 0 2px 0 #ff3c5a;
      letter-spacing: 0.04em;
    }

    #${FAKE_NEWS_BANNER_ID}::before {
      content: '';
      position: absolute;
      bottom: 0; left: 0; right: 0; height: 1px;
      background: linear-gradient(90deg, transparent, #ff3c5a 30%, #ff3c5a 70%, transparent);
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-icon {
      font-size: 15px;
      flex-shrink: 0;
      color: #ff3c5a;
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-badge {
      font-family: 'Share Tech Mono', monospace;
      font-size: 9px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      padding: 3px 8px;
      border: 1px solid #ff3c5a;
      border-radius: 4px;
      color: #ff3c5a;
      background: rgba(255,60,90,0.10);
      flex-shrink: 0;
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-msg {
      flex: 1;
      color: #e2eeff;
      font-size: 13px;
      font-weight: 600;
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-msg span {
      color: #4a6080;
      font-weight: 400;
      font-family: 'Share Tech Mono', monospace;
      font-size: 11px;
      margin-left: 8px;
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-close {
      cursor: pointer;
      background: transparent;
      border: 1px solid #1e3a5f;
      color: #4a6080;
      border-radius: 4px;
      padding: 3px 10px;
      font-family: 'Share Tech Mono', monospace;
      font-size: 10px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      transition: border-color 0.2s, color 0.2s;
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-close:hover {
      border-color: #ff3c5a;
      color: #ff3c5a;
    }

    /* ── Fake news highlight on page ── */
    .${FAKE_NEWS_HIGHLIGHT_CLASS} {
      outline: 2px solid rgba(255, 60, 90, 0.5) !important;
      outline-offset: 6px !important;
      border-radius: 4px !important;
      background-color: rgba(255, 60, 90, 0.04) !important;
      position: relative !important;
    }

    .${FAKE_NEWS_LABEL_CLASS} {
      display: inline-block;
      position: absolute;
      top: -18px;
      left: 0;
      background: #0a0e1a;
      color: #ff3c5a;
      font-family: 'Share Tech Mono', monospace;
      font-size: 10px;
      font-weight: 400;
      letter-spacing: 0.10em;
      text-transform: uppercase;
      padding: 3px 10px;
      border: 1px solid #ff3c5a;
      border-bottom: none;
      border-radius: 4px 4px 0 0;
      z-index: 2147483646;
      pointer-events: none;
      white-space: nowrap;
    }

    /* ── Selection Popup ── */
    #ai-security-selection-popup {
      position: fixed;
      z-index: 2147483647;
      width: 272px;
      background: #0a0e1a;
      color: #c9d8ef;
      font-family: 'Rajdhani', sans-serif;
      font-size: 13px;
      border-radius: 10px;
      border: 1px solid #1e3a5f;
      box-shadow:
        0 0 0 1px rgba(0,212,255,0.08),
        0 8px 32px rgba(0,0,0,0.7),
        0 0 20px rgba(0,212,255,0.06);
      padding: 0;
      pointer-events: none;
      opacity: 0;
      transform: translateY(4px);
      transition: opacity 0.18s ease, transform 0.18s ease;
      overflow: hidden;
    }

    #ai-security-selection-popup::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 1px;
      background: linear-gradient(90deg, transparent, rgba(0,212,255,0.4), transparent);
    }

    #ai-security-selection-popup.visible {
      opacity: 1;
      pointer-events: auto;
      transform: translateY(0);
    }

    /* popup top bar */
    #ai-security-selection-popup .ai-sel-topbar {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 9px 12px 8px;
      border-bottom: 1px solid #1e3a5f;
      background: rgba(13, 21, 38, 0.9);
    }

    #ai-security-selection-popup .ai-sel-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    #ai-security-selection-popup .ai-sel-dot.fake  { background: #ff3c5a; box-shadow: 0 0 6px #ff3c5a; animation: ai-sel-pulse 1s infinite; }
    #ai-security-selection-popup .ai-sel-dot.safe  { background: #00ff9d; box-shadow: 0 0 6px #00ff9d; }
    #ai-security-selection-popup .ai-sel-dot.loading { background: #00d4ff; box-shadow: 0 0 6px #00d4ff; animation: ai-sel-pulse 0.8s infinite; }

    @keyframes ai-sel-pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }

    #ai-security-selection-popup .ai-sel-header {
      font-family: 'Rajdhani', sans-serif;
      font-weight: 700;
      font-size: 13px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    #ai-security-selection-popup .ai-sel-header.fake    { color: #ff3c5a; }
    #ai-security-selection-popup .ai-sel-header.safe    { color: #00ff9d; }
    #ai-security-selection-popup .ai-sel-header.loading { color: #00d4ff; }

    #ai-security-selection-popup .ai-sel-tag {
      margin-left: auto;
      font-family: 'Share Tech Mono', monospace;
      font-size: 8px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      padding: 2px 6px;
      border-radius: 3px;
    }

    #ai-security-selection-popup .ai-sel-tag.fake { border: 1px solid #ff3c5a; color: #ff3c5a; background: rgba(255,60,90,0.1); }
    #ai-security-selection-popup .ai-sel-tag.safe { border: 1px solid #00ff9d; color: #00ff9d; background: rgba(0,255,157,0.08); }

    /* popup body */
    #ai-security-selection-popup .ai-sel-body {
      padding: 10px 12px 11px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    #ai-security-selection-popup .ai-sel-reasons {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    #ai-security-selection-popup .ai-sel-reasons li {
      font-family: 'Rajdhani', sans-serif;
      font-size: 12px;
      font-weight: 400;
      color: #c9d8ef;
      background: #111827;
      border: 1px solid #1e3a5f;
      border-radius: 4px;
      padding: 5px 9px;
      letter-spacing: 0.02em;
      line-height: 1.4;
      opacity: 0.85;
    }

    /* risk bar */
    #ai-security-selection-popup .ai-sel-risk-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    #ai-security-selection-popup .ai-sel-risk-label {
      font-family: 'Share Tech Mono', monospace;
      font-size: 9px;
      color: #4a6080;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      white-space: nowrap;
    }

    #ai-security-selection-popup .ai-sel-risk-track {
      flex: 1;
      height: 4px;
      background: rgba(255,255,255,0.05);
      border-radius: 2px;
      overflow: hidden;
    }

    #ai-security-selection-popup .ai-sel-risk-fill {
      height: 100%;
      border-radius: 2px;
      transition: width 0.6s cubic-bezier(0.16,1,0.3,1);
    }

    #ai-security-selection-popup .ai-sel-risk-val {
      font-family: 'Share Tech Mono', monospace;
      font-size: 10px;
      min-width: 28px;
      text-align: right;
    }

    /* popup scanline overlay */
    #ai-security-selection-popup::after {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,212,255,0.012) 2px, rgba(0,212,255,0.012) 4px);
      pointer-events: none;
      border-radius: 10px;
    }
  `;
  document.documentElement.appendChild(style);
}

// ── Link scanning ─────────────────────────────────────────────────────────────
const seenElements = new WeakSet();

function isHttpUrl(url) {
  return /^https?:\/\//i.test(url);
}

function getLinksToScan() {
  const links = [];

  for (const anchor of document.querySelectorAll("a[href]")) {
    const url = anchor.href;

    if (!isHttpUrl(url) || seenElements.has(anchor)) {
      continue;
    }

    seenElements.add(anchor);
    links.push({ url, anchor });

    if (links.length >= SCAN_LIMIT) {
      break;
    }
  }

  return links;
}

function buildWarningTitle(result) {
  const reasons = result.data.reasons || [];

  if (reasons.length === 0) {
    return "AI Security: suspicious link.";
  }

  return `AI Security: suspicious link. ${reasons.join("; ")}`;
}

function markLink(anchor, result) {
  anchor.classList.remove(SAFE_CLASS, WARNING_CLASS);

  if (!result.ok) {
    return;
  }

  if (result.data.risk_score >= 30 || result.data.is_phishing) {
    anchor.classList.add(WARNING_CLASS);
    anchor.dataset.aiSecurityRiskScore = String(result.data.risk_score);
    anchor.title = buildWarningTitle(result);
    return;
  }

  anchor.classList.add(SAFE_CLASS);
}

async function scanPageLinks() {
  const links = getLinksToScan();

  if (links.length === 0) {
    return;
  }

  let results;

  try {
    results = await chrome.runtime.sendMessage({
      type: "ANALYZE_URLS",
      urls: links.map(link => link.url),
    });
  } catch (error) {
    return;
  }

  if (!Array.isArray(results)) {
    return;
  }

  results.forEach((result, index) => {
    markLink(links[index].anchor, result);
  });
}

// ── Fake-news page scanning ───────────────────────────────────────────────────

function showFakeNewsBanner(data) {
  if (document.getElementById(FAKE_NEWS_BANNER_ID)) {
    return;
  }

  const confidence = typeof data.ml_confidence === "number"
    ? `${Math.round(data.ml_confidence * 100)}% confidence`
    : null;

  const reason = data.reasons && data.reasons.length ? data.reasons[0] : null;

  const banner = document.createElement("div");
  banner.id = FAKE_NEWS_BANNER_ID;
  banner.innerHTML = `
    <span class="ai-sec-icon">⚠</span>
    <span class="ai-sec-badge">Fake News</span>
    <span class="ai-sec-msg">
      Misleading content detected on this page
      ${reason ? `<span>— ${reason}</span>` : ""}
    </span>
    ${confidence ? `<span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:.06em;flex-shrink:0;">${confidence}</span>` : ""}
    <button class="ai-sec-close" id="ai-security-close-banner">DISMISS</button>
  `;

  document.body.insertBefore(banner, document.body.firstChild);

  document.getElementById("ai-security-close-banner").addEventListener("click", () => {
    banner.remove();
  });
}

function applyHighlight(el, labelText) {
  if (el.querySelector(`.${FAKE_NEWS_LABEL_CLASS}`)) return;
  el.classList.add(FAKE_NEWS_HIGHLIGHT_CLASS);
  if (window.getComputedStyle(el).position === "static") el.style.position = "relative";
  const label = document.createElement("span");
  label.className = FAKE_NEWS_LABEL_CLASS;
  label.textContent = labelText;
  el.insertBefore(label, el.firstChild);
}

function highlightFakeNewsContent(data) {
  const score = data.risk_score != null ? ` · ${data.risk_score}% risk` : "";
  const labelText = `⚠ Fake News${score}`;

  let cards = [];
  for (const sel of CARD_SELECTORS) {
    const found = [...document.querySelectorAll(sel)].filter(
      el => !el.closest(`.${FAKE_NEWS_HIGHLIGHT_CLASS}`) &&
            el.innerText && el.innerText.trim().split(/\s+/).length >= 5
    );
    if (found.length >= 2) { cards = found.slice(0, 30); break; }
  }

  if (cards.length > 0) {
    cards.forEach(card => applyHighlight(card, labelText));
    return;
  }

  for (const sel of ARTICLE_SELECTORS) {
    const el = document.querySelector(sel);
    if (el && el.innerText && el.innerText.trim().split(/\s+/).length >= MIN_ARTICLE_WORDS) {
      applyHighlight(el, `⚠ Fake News Detected${score}`);
      return;
    }
  }
}

async function scanPageContent() {
  const title = document.title || "";
  const bodyText = (document.body && document.body.innerText) || "";
  const wordCount = bodyText.trim().split(/\s+/).length;

  if (wordCount < MIN_ARTICLE_WORDS) {
    return;
  }

  let result;
  try {
    result = await chrome.runtime.sendMessage({
      type: "ANALYZE_CONTENT",
      title,
      bodyText: bodyText.slice(0, 8000),
      sourceUrl: window.location.href,
    });
  } catch (error) {
    return;
  }

  if (result && result.ok && result.data && result.data.is_fake_news) {
    showFakeNewsBanner(result.data);
    highlightFakeNewsContent(result.data);
  }
}

// ── Selection popup ───────────────────────────────────────────────────────────

const SELECTION_POPUP_ID = "ai-security-selection-popup";
const MIN_SELECTION_WORDS = 5;
let selectionDebounceTimer = null;
let lastSelectedText = "";

function getOrCreateSelectionPopup() {
  let popup = document.getElementById(SELECTION_POPUP_ID);
  if (!popup) {
    popup = document.createElement("div");
    popup.id = SELECTION_POPUP_ID;
    document.documentElement.appendChild(popup);
  }
  return popup;
}

function positionPopup(popup, rect) {
  const GAP = 10;
  let top = rect.bottom + window.scrollY + GAP;
  let left = rect.left + window.scrollX;
  const maxLeft = window.innerWidth - 288;
  left = Math.max(8, Math.min(left, maxLeft));
  if (rect.bottom + 160 > window.innerHeight) top = rect.top + window.scrollY - 160 - GAP;
  popup.style.top = `${Math.max(8, top)}px`;
  popup.style.left = `${left}px`;
  popup.style.position = "fixed";
  // Revert to fixed positioning relative to viewport
  popup.style.top = `${Math.max(8, rect.bottom + GAP)}px`;
  popup.style.left = `${Math.max(8, Math.min(rect.left, maxLeft))}px`;
  if (rect.bottom + 160 > window.innerHeight) {
    popup.style.top = `${Math.max(8, rect.top - 160 - GAP)}px`;
  }
}

function riskColor(score) {
  if (score > 70) return "#ff3c5a";
  if (score > 40) return "#ffaa00";
  return "#00ff9d";
}

function buildSelectionPopupHTML(state, data) {
  if (state === "loading") {
    return `
      <div class="ai-sel-topbar">
        <div class="ai-sel-dot loading"></div>
        <div class="ai-sel-header loading">Analyzing</div>
        <span class="ai-sel-tag" style="border:1px solid #1e3a5f;color:#4a6080;background:transparent;margin-left:auto;">SCANNING</span>
      </div>
      <div class="ai-sel-body">
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:.06em;">Processing selected text...</div>
      </div>
    `;
  }

  if (state === "error") {
    return `
      <div class="ai-sel-topbar">
        <div class="ai-sel-dot" style="background:#ffaa00;box-shadow:0 0 6px #ffaa00;"></div>
        <div class="ai-sel-header" style="color:#ffaa00;">Backend Offline</div>
      </div>
      <div class="ai-sel-body">
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:.06em;">Start the local API and try again.</div>
      </div>
    `;
  }

  const isFake = data.is_fake_news;
  const score = data.risk_score != null ? data.risk_score : null;
  const color = score != null ? riskColor(score) : (isFake ? "#ff3c5a" : "#00ff9d");
  const reasons = (data.reasons || []).slice(0, 3);

  const reasonsHtml = reasons.length
    ? `<ul class="ai-sel-reasons">${reasons.map(r => `<li>${r}</li>`).join("")}</ul>`
    : "";

  const barHtml = score != null ? `
    <div class="ai-sel-risk-row">
      <span class="ai-sel-risk-label">Risk</span>
      <div class="ai-sel-risk-track">
        <div class="ai-sel-risk-fill" style="width:${score}%;background:${color};"></div>
      </div>
      <span class="ai-sel-risk-val" style="color:${color};">${score}<span style="color:#4a6080;font-size:8px;">/100</span></span>
    </div>
  ` : "";

  return `
    <div class="ai-sel-topbar">
      <div class="ai-sel-dot ${isFake ? "fake" : "safe"}"></div>
      <div class="ai-sel-header ${isFake ? "fake" : "safe"}">${isFake ? "Fake / Misleading" : "Looks Reliable"}</div>
      <span class="ai-sel-tag ${isFake ? "fake" : "safe"}">${isFake ? "THREAT" : "CLEAR"}</span>
    </div>
    <div class="ai-sel-body">
      ${reasonsHtml}
      ${barHtml}
    </div>
  `;
}

function showSelectionPopup(text, rect) {
  const popup = getOrCreateSelectionPopup();
  positionPopup(popup, rect);
  popup.innerHTML = buildSelectionPopupHTML("loading", null);
  popup.classList.add("visible");

  const words = text.trim().split(/\s+/);
  const paddedText = words.length < 20
    ? text + " " + Array(20 - words.length).fill("content").join(" ")
    : text;

  chrome.runtime.sendMessage({
    type: "ANALYZE_CONTENT",
    title: "",
    bodyText: paddedText.slice(0, 2000),
    sourceUrl: window.location.href,
  }).then(result => {
    const p = document.getElementById(SELECTION_POPUP_ID);
    if (!p) return;

    if (!result || !result.ok) {
      p.innerHTML = buildSelectionPopupHTML("error", null);
      return;
    }

    p.innerHTML = buildSelectionPopupHTML("result", result.data);
  }).catch(() => {
    const p = document.getElementById(SELECTION_POPUP_ID);
    if (p) p.innerHTML = buildSelectionPopupHTML("error", null);
  });
}

function hideSelectionPopup() {
  const popup = document.getElementById(SELECTION_POPUP_ID);
  if (popup) popup.classList.remove("visible");
}

document.addEventListener("selectionchange", () => {
  const sel = window.getSelection();
  lastSelectedText = sel ? sel.toString().trim() : "";
});

document.addEventListener("mouseup", (e) => {
  if (e.button !== 0) return;
  if (e.target.closest(`#${SELECTION_POPUP_ID}`)) return;

  clearTimeout(selectionDebounceTimer);
  selectionDebounceTimer = setTimeout(() => {
    const text = lastSelectedText;
    const wordCount = text.split(/\s+/).filter(Boolean).length;
    if (wordCount < MIN_SELECTION_WORDS) {
      hideSelectionPopup();
      return;
    }
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    showSelectionPopup(text, rect);
  }, 150);
});

document.addEventListener("mousedown", (e) => {
  if (e.button !== 0) return;
  if (e.target.closest(`#${SELECTION_POPUP_ID}`)) return;
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel || sel.toString().trim().length === 0) hideSelectionPopup();
  }, 200);
});

// ── Scheduler ─────────────────────────────────────────────────────────────────
let contentScanDone = false;
let isScanning = false;

function scheduleScan() {
  if (isScanning) return;

  window.clearTimeout(scheduleScan.timer);
  scheduleScan.timer = window.setTimeout(async () => {
    isScanning = true;
    try {
      await scanPageLinks();

      if (!contentScanDone) {
        contentScanDone = true;
        await scanPageContent();
      }
    } finally {
      isScanning = false;
    }
  }, 1000);
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
injectStyles();
scheduleScan();

const observer = new MutationObserver(scheduleScan);
observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});