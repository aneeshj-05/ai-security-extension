importScripts("../config/constants.js", "../utils/api.js");

const resultCache = new Map();
const CACHE_TTL_MS = 5 * 60 * 1000;

function canAnalyzeUrl(url) {
  return typeof url === "string" && /^https?:\/\//i.test(url);
}

function getCachedResult(url) {
  const cached = resultCache.get(url);
  if (!cached) return null;
  if (Date.now() - cached.createdAt > CACHE_TTL_MS) {
    resultCache.delete(url);
    return null;
  }
  return cached.result;
}

function setCachedResult(url, result) {
  resultCache.set(url, { createdAt: Date.now(), result });
}

async function analyzeWithCache(url) {
  if (!canAnalyzeUrl(url)) {
    return { ok: false, code: "UNSUPPORTED_URL", message: "Only http and https URLs can be analyzed." };
  }
  const cached = getCachedResult(url);
  if (cached) return cached;
  const result = await globalThis.AiSecurityApi.analyzeUrl(url);
  setCachedResult(url, result);
  return result;
}

async function analyzeManyWithCache(urls) {
  const results = new Array(urls.length);
  const urlsToFetch = [];
  const resultIndexes = [];

  urls.forEach((url, index) => {
    if (!canAnalyzeUrl(url)) {
      results[index] = { ok: false, code: "UNSUPPORTED_URL", message: "Only http and https URLs can be analyzed." };
      return;
    }
    const cached = getCachedResult(url);
    if (cached) { results[index] = cached; return; }
    urlsToFetch.push(url);
    resultIndexes.push(index);
  });

  if (urlsToFetch.length === 0) return results;

  const fetchedResults = await globalThis.AiSecurityApi.analyzeUrlsBatch(urlsToFetch);
  fetchedResults.forEach((result, fetchIndex) => {
    const originalIndex = resultIndexes[fetchIndex];
    results[originalIndex] = result;
    setCachedResult(urlsToFetch[fetchIndex], result);
  });

  return results;
}

// Draw a small dot directly onto the icon — no badge box
async function setIconWithDot(tabId, dotColor) {
  try {
    const size = 32;
    const canvas = new OffscreenCanvas(size, size);
    const ctx = canvas.getContext("2d");

    const response = await fetch(chrome.runtime.getURL("icons/icon32.png"));
    const blob = await response.blob();
    const bitmap = await createImageBitmap(blob);
    ctx.drawImage(bitmap, 0, 0, size, size);

    if (dotColor) {
      const r = 6;
      const cx = size - r - 1;
      const cy = size - r - 1;
      // White outline ring
      ctx.beginPath();
      ctx.arc(cx, cy, r + 1.5, 0, Math.PI * 2);
      ctx.fillStyle = "white";
      ctx.fill();
      // Colored dot
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = dotColor;
      ctx.fill();
    }

    const imageData = ctx.getImageData(0, 0, size, size);
    await chrome.action.setIcon({ tabId, imageData });
    await chrome.action.setBadgeText({ tabId, text: "" });
  } catch (e) {
    // Fallback: just clear badge
    await chrome.action.setBadgeText({ tabId, text: "" });
  }
}

async function updateBadge(tabId, result) {
  if (!result.ok) { await setIconWithDot(tabId, null); return; }
  if (result.data.is_phishing) { await setIconWithDot(tabId, "#dc2626"); return; }
  await setIconWithDot(tabId, "#16a34a");
}

async function scanTab(tabId, url) {
  if (!canAnalyzeUrl(url)) return;
  const result = await analyzeWithCache(url);
  await updateBadge(tabId, result);
  await chrome.storage.local.set({
    [`tab:${tabId}`]: { url, checkedAt: Date.now(), result },
  });
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  const url = changeInfo.url || tab.url;
  if (changeInfo.status === "loading" && canAnalyzeUrl(url)) {
    setIconWithDot(tabId, "#2563eb");
  }
  if (changeInfo.status === "complete" && canAnalyzeUrl(url)) {
    scanTab(tabId, url);
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ANALYZE_URL") {
    analyzeWithCache(message.url)
      .then(sendResponse)
      .catch(error => sendResponse({ ok: false, code: "BACKGROUND_ERROR", message: error.message || "Unable to analyze URL." }));
    return true;
  }

  if (message.type === "ANALYZE_URLS") {
    analyzeManyWithCache(message.urls)
      .then(sendResponse)
      .catch(error => sendResponse(message.urls.map(() => ({ ok: false, code: "BACKGROUND_ERROR", message: error.message || "Unable to analyze URL." }))));
    return true;
  }

  if (message.type === "ANALYZE_CONTENT") {
    globalThis.AiSecurityApi.analyzeContent(message.title, message.bodyText, message.sourceUrl)
      .then(async (result) => {
        if (result.ok && result.data.is_fake_news && sender.tab) {
          await setIconWithDot(sender.tab.id, "#dc2626");
          const tabKey = `tab:${sender.tab.id}`;
          const current = await chrome.storage.local.get(tabKey);
          if (current[tabKey]) {
            await chrome.storage.local.set({ [tabKey]: { ...current[tabKey], newsResult: result } });
          }
        }
        sendResponse(result);
      })
      .catch(error => sendResponse({ ok: false, code: "BACKGROUND_ERROR", message: error.message || "Unable to analyze page content." }));
    return true;
  }

  return false;
});
