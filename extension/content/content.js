const SCAN_LIMIT = globalThis.AI_SECURITY_CONFIG.LINK_SCAN_LIMIT;
const WARNING_CLASS = "ai-security-suspicious-link";
const SAFE_CLASS = "ai-security-safe-link";
const FAKE_NEWS_BANNER_ID = "ai-security-fake-news-banner";
const MIN_ARTICLE_WORDS = 20;

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
      bodyText: bodyText.slice(0, 8000), // cap to avoid huge payloads
    });
  } catch (error) {
    return;
  }

  if (result && result.ok && result.data && result.data.is_fake_news) {
    showFakeNewsBanner(result.data);
  }
}

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
