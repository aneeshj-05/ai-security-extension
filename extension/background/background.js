importScripts("../config/constants.js", "../utils/api.js");

const resultCache = new Map();
const CACHE_TTL_MS = 5 * 60 * 1000;

function canAnalyzeUrl(url) {
  return typeof url === "string" && /^https?:\/\//i.test(url);
}

function getCachedResult(url) {
  const cached = resultCache.get(url);

  if (!cached) {
    return null;
  }

  if (Date.now() - cached.createdAt > CACHE_TTL_MS) {
    resultCache.delete(url);
    return null;
  }

  return cached.result;
}

function setCachedResult(url, result) {
  resultCache.set(url, {
    createdAt: Date.now(),
    result,
  });
}

async function analyzeWithCache(url) {
  if (!canAnalyzeUrl(url)) {
    return {
      ok: false,
      code: "UNSUPPORTED_URL",
      message: "Only http and https URLs can be analyzed.",
    };
  }

  const cached = getCachedResult(url);

  if (cached) {
    return cached;
  }

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
      results[index] = {
        ok: false,
        code: "UNSUPPORTED_URL",
        message: "Only http and https URLs can be analyzed.",
      };
      return;
    }

    const cached = getCachedResult(url);

    if (cached) {
      results[index] = cached;
      return;
    }

    urlsToFetch.push(url);
    resultIndexes.push(index);
  });

  if (urlsToFetch.length === 0) {
    return results;
  }

  const fetchedResults = await globalThis.AiSecurityApi.analyzeUrlsBatch(urlsToFetch);

  fetchedResults.forEach((result, fetchIndex) => {
    const originalIndex = resultIndexes[fetchIndex];
    const url = urlsToFetch[fetchIndex];

    results[originalIndex] = result;
    setCachedResult(url, result);
  });

  return results;
}

async function updateBadge(tabId, result) {
  if (!result.ok) {
    await chrome.action.setBadgeText({ tabId, text: "!" });
    await chrome.action.setBadgeBackgroundColor({ tabId, color: "#6b7280" });
    return;
  }

  if (result.data.is_phishing) {
    await chrome.action.setBadgeText({ tabId, text: "!" });
    await chrome.action.setBadgeBackgroundColor({ tabId, color: "#dc2626" });
    return;
  }

  await chrome.action.setBadgeText({ tabId, text: "OK" });
  await chrome.action.setBadgeBackgroundColor({ tabId, color: "#16a34a" });
}

async function scanTab(tabId, url) {
  if (!canAnalyzeUrl(url)) {
    return;
  }

  const result = await analyzeWithCache(url);
  await updateBadge(tabId, result);

  await chrome.storage.local.set({
    [`tab:${tabId}`]: {
      url,
      checkedAt: Date.now(),
      result,
    },
  });
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  const url = changeInfo.url || tab.url;

  if (changeInfo.status === "loading" && canAnalyzeUrl(url)) {
    chrome.action.setBadgeText({ tabId, text: "..." });
    chrome.action.setBadgeBackgroundColor({ tabId, color: "#2563eb" });
  }

  if (changeInfo.status === "complete" && canAnalyzeUrl(url)) {
    scanTab(tabId, url);
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ANALYZE_URL") {
    analyzeWithCache(message.url)
      .then(sendResponse)
      .catch(error => {
        sendResponse({
          ok: false,
          code: "BACKGROUND_ERROR",
          message: error.message || "Unable to analyze URL.",
        });
      });
    return true;
  }

  if (message.type === "ANALYZE_URLS") {
    analyzeManyWithCache(message.urls)
      .then(sendResponse)
      .catch(error => {
        sendResponse(
          message.urls.map(() => ({
            ok: false,
            code: "BACKGROUND_ERROR",
            message: error.message || "Unable to analyze URL.",
          }))
        );
      });
    return true;
  }

  if (message.type === "ANALYZE_CONTENT") {
    globalThis.AiSecurityApi.analyzeContent(message.title, message.bodyText, message.sourceUrl)
      .then(async (result) => {
        if (result.ok && result.data.is_fake_news && sender.tab) {
          await chrome.action.setBadgeText({ tabId: sender.tab.id, text: "!" });
          await chrome.action.setBadgeBackgroundColor({ tabId: sender.tab.id, color: "#f59e0b" });
          
          const tabKey = `tab:${sender.tab.id}`;
          const current = await chrome.storage.local.get(tabKey);
          if (current[tabKey]) {
            await chrome.storage.local.set({
              [tabKey]: {
                ...current[tabKey],
                newsResult: result
              }
            });
          }
        }
        sendResponse(result);
      })
      .catch(error => {
        sendResponse({
          ok: false,
          code: "BACKGROUND_ERROR",
          message: error.message || "Unable to analyze page content.",
        });
      });
    return true;
  }

  return false;
});
