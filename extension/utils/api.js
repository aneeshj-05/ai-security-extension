async function analyzeUrl(url) {
  const result = await requestJson("/api/v1/analyze-url", { url });

  if (!result.ok) {
    return result;
  }

  return {
    ok: true,
    data: result.data,
  };
}

async function analyzeUrlsBatch(urls) {
  const result = await requestJson(
    "/api/v1/analyze-urls-batch",
    urls.map(url => ({ url })),
    globalThis.AI_SECURITY_CONFIG.BATCH_API_TIMEOUT_MS
  );

  if (!result.ok) {
    return urls.map(() => result);
  }

  return result.data.map(data => ({
    ok: true,
    data,
  }));
}

async function analyzeContent(title, bodyText) {
  const result = await requestJson(
    "/api/v1/analyze-content",
    { title, body_text: bodyText },
    globalThis.AI_SECURITY_CONFIG.API_TIMEOUT_MS
  );

  if (!result.ok) {
    return result;
  }

  return {
    ok: true,
    data: result.data,
  };
}

async function requestJson(path, body, timeoutMs = globalThis.AI_SECURITY_CONFIG.API_TIMEOUT_MS) {
  const config = globalThis.AI_SECURITY_CONFIG;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${config.API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    const data = await response.json();

    if (!response.ok) {
      const detail = data.detail || {};
      let message = detail.message || "The backend could not analyze this URL.";

      if (detail.errors && detail.errors.length > 0) {
        message = detail.errors[0].msg || message;
      }

      return {
        ok: false,
        status: response.status,
        code: detail.code || "API_ERROR",
        message,
      };
    }

    return {
      ok: true,
      data,
    };
  } catch (error) {
    return {
      ok: false,
      status: 0,
      code: error.name === "AbortError" ? "API_TIMEOUT" : "API_UNAVAILABLE",
      message:
        error.name === "AbortError"
          ? "Backend request timed out."
          : "Backend unavailable. Start the local API and try again.",
    };
  } finally {
    clearTimeout(timeoutId);
  }
}

globalThis.AiSecurityApi = {
  analyzeUrl,
  analyzeUrlsBatch,
  analyzeContent,
};

