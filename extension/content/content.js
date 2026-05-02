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
    .${WARNING_CLASS} {
      outline: 2px solid #dc2626 !important;
      outline-offset: 2px !important;
      background-color: rgba(220, 38, 38, 0.12) !important;
      border-radius: 3px !important;
    }

    .${WARNING_CLASS}::after {
      content: " suspicious";
      color: #dc2626;
      font-size: 11px;
      font-weight: 700;
      margin-left: 4px;
    }

    #${FAKE_NEWS_BANNER_ID} {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 2147483647;
      background: #7f1d1d;
      color: #fef2f2;
      font-family: system-ui, sans-serif;
      font-size: 14px;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.5);
    }

    #${FAKE_NEWS_BANNER_ID} .ai-sec-icon { font-size: 18px; flex-shrink: 0; }
    #${FAKE_NEWS_BANNER_ID} .ai-sec-msg  { flex: 1; }
    #${FAKE_NEWS_BANNER_ID} .ai-sec-close {
      cursor: pointer;
      background: transparent;
      border: 1px solid #fca5a5;
      color: #fef2f2;
      border-radius: 4px;
      padding: 2px 8px;
      font-size: 12px;
    }

    .${FAKE_NEWS_HIGHLIGHT_CLASS} {
      outline: 3px solid #dc2626 !important;
      outline-offset: 6px !important;
      border-radius: 4px !important;
      background-color: rgba(220, 38, 38, 0.06) !important;
      position: relative !important;
    }

    .${FAKE_NEWS_LABEL_CLASS} {
      display: inline-block;
      position: absolute;
      top: -14px;
      left: 0;
      background: #dc2626;
      color: #fff;
      font-family: system-ui, sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      padding: 2px 8px;
      border-radius: 3px 3px 0 0;
      z-index: 2147483646;
      pointer-events: none;
      white-space: nowrap;
    }

    #ai-security-selection-popup {
      position: fixed;
      z-index: 2147483647;
      max-width: 280px;
      background: #1c1c1e;
      color: #f5f5f7;
      font-family: system-ui, sans-serif;
      font-size: 12px;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.5);
      padding: 10px 12px;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.15s ease;
    }

    #ai-security-selection-popup.visible {
      opacity: 1;
      pointer-events: auto;
    }

    #ai-security-selection-popup .ai-sel-header {
      font-weight: 700;
      font-size: 12px;
      margin-bottom: 5px;
      display: flex;
      align-items: center;
      gap: 5px;
    }

    #ai-security-selection-popup .ai-sel-header.fake { color: #f87171; }
    #ai-security-selection-popup .ai-sel-header.safe { color: #4ade80; }
    #ai-security-selection-popup .ai-sel-header.loading { color: #93c5fd; }

    #ai-security-selection-popup .ai-sel-reasons {
      margin: 0;
      padding: 0 0 0 14px;
      color: #d1d5db;
      font-size: 11px;
      line-height: 1.5;
    }

    #ai-security-selection-popup .ai-sel-score {
      margin-top: 5px;
      font-size: 11px;
      color: #9ca3af;
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
    return "AI Security Assistant: suspicious link.";
  }

  return `AI Security Assistant: suspicious link. ${reasons.join("; ")}`;
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
    return; // already shown
  }

  const confidence = typeof data.ml_confidence === "number"
    ? ` (${Math.round(data.ml_confidence * 100)}% confidence)`
    : "";

  const banner = document.createElement("div");
  banner.id = FAKE_NEWS_BANNER_ID;
  banner.innerHTML = `
    <span class="ai-sec-icon">⚠️</span>
    <span class="ai-sec-msg">
      <strong>AI Security: Possible Fake News Detected${confidence}</strong>
      ${data.reasons && data.reasons.length ? " — " + data.reasons[0] : ""}
    </span>
    <button class="ai-sec-close" id="ai-security-close-banner">Dismiss</button>
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
  const labelText = `⚠️ Fake News${score}`;

  // 1. Try to find individual cards first (homepage / listing page)
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

  // 2. Fallback: highlight the single article container
  for (const sel of ARTICLE_SELECTORS) {
    const el = document.querySelector(sel);
    if (el && el.innerText && el.innerText.trim().split(/\s+/).length >= MIN_ARTICLE_WORDS) {
      applyHighlight(el, `⚠️ AI Security: Fake News Detected${score}`);
      return;
    }
  }
}

async function scanPageContent() {
  // Only scan pages that look like articles (have enough text)
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
let isDragging = false;
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
  const GAP = 8;
  let top = rect.bottom + GAP;
  let left = rect.left;
  const maxLeft = window.innerWidth - 296;
  left = Math.max(8, Math.min(left, maxLeft));
  if (top + 130 > window.innerHeight) top = rect.top - 130 - GAP;
  popup.style.top = `${Math.max(8, top)}px`;
  popup.style.left = `${left}px`;
}

function showSelectionPopup(text, rect) {
  const popup = getOrCreateSelectionPopup();
  positionPopup(popup, rect);
  popup.innerHTML = `<div class="ai-sel-header loading">⏳ Analyzing…</div>`;
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
      p.innerHTML = `<div class="ai-sel-header">⚠️ Backend unavailable</div>`;
      return;
    }
    const d = result.data;
    const isFake = d.is_fake_news;
    const icon = isFake ? "🚨" : "✅";
    const verdict = isFake ? "Fake / Misleading" : "Looks Reliable";
    const reasons = (d.reasons || []).slice(0, 3);
    const reasonsHtml = reasons.length
      ? `<ul class="ai-sel-reasons">${reasons.map(r => `<li>${r}</li>`).join("")}</ul>` : "";
    const score = d.risk_score != null ? `<div class="ai-sel-score">Risk score: ${d.risk_score}/100</div>` : "";
    p.innerHTML = `<div class="ai-sel-header ${isFake ? "fake" : "safe"}">${icon} ${verdict}</div>${reasonsHtml}${score}`;
  }).catch(() => {
    const p = document.getElementById(SELECTION_POPUP_ID);
    if (p) p.innerHTML = `<div class="ai-sel-header">⚠️ Error analyzing</div>`;
  });
}

function hideSelectionPopup() {
  const popup = document.getElementById(SELECTION_POPUP_ID);
  if (popup) popup.classList.remove("visible");
}

// Use selectionchange (fires whenever selection changes) + mouseup to confirm drag ended
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
  // Only hide if clicking outside — delay to not race with mouseup
  setTimeout(() => {
    const sel = window.getSelection();
    if (!sel || sel.toString().trim().length === 0) hideSelectionPopup();
  }, 200);
});

// ── Scheduler ─────────────────────────────────────────────────────────────────
let contentScanDone = false;
let isScanning = false;

function scheduleScan() {
  if (isScanning) return; // Drop overlapping triggers while actively scanning

  window.clearTimeout(scheduleScan.timer);
  scheduleScan.timer = window.setTimeout(async () => {
    isScanning = true;
    try {
      await scanPageLinks();

      // Run content scan once per page load
      if (!contentScanDone) {
        contentScanDone = true;
        await scanPageContent();
      }
    } finally {
      isScanning = false;
    }
  }, 1000); // 1-second debounce
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
injectStyles();
scheduleScan();

const observer = new MutationObserver(scheduleScan);
observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});
