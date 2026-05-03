document.addEventListener("DOMContentLoaded", async () => {
  const statusEl       = document.getElementById("status");
  const statusBanner   = document.getElementById("status-banner");
  const statusDot      = document.getElementById("status-dot");
  const verdictEl      = document.getElementById("verdict");
  const metricsRow     = document.getElementById("metrics-row");
  const scoreNum       = document.getElementById("score-num");
  const riskLevelVal   = document.getElementById("risk-level-val");
  const scoreSub       = document.getElementById("score-sub");
  const riskBarSection = document.getElementById("risk-bar-section");
  const riskBar        = document.getElementById("risk-bar");
  const barPct         = document.getElementById("bar-pct");
  const summaryLine    = document.getElementById("summary-line");
  const reasonsSection = document.getElementById("reasons-section");
  const reasonsList    = document.getElementById("reasons");
  const aiConf         = document.getElementById("ai-conf");
  const aiConfVal      = document.getElementById("ai-conf-val");
  const newsContainer  = document.getElementById("news-section-container");

  // ── Helpers ──────────────────────────────────────────
  function setStatus(text, color) {
    statusEl.textContent = text;
    statusBanner.style.setProperty("--status-color", color);
    statusDot.style.background = color;
    statusDot.style.boxShadow = `0 0 8px ${color}`;
    statusBanner.classList.remove("status-analyzing");
  }

  function riskColor(score) {
    if (score > 70) return "var(--cyber-danger)";
    if (score > 40) return "var(--cyber-warn)";
    return "var(--cyber-accent2)";
  }

  function riskLabel(score) {
    if (score > 70) return "HIGH";
    if (score > 40) return "MODERATE";
    return "LOW";
  }

  // ── Main ─────────────────────────────────────────────
  try {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    let url = tab.url;

    if (!url || !url.startsWith("http")) {
      setStatus("No Page Detected", "var(--cyber-muted)");
      statusEl.style.fontSize = "13px";
      return;
    }

    const result = await globalThis.AiSecurityApi.analyzeUrl(url);

    if (!result.ok) {
      setStatus("⚠ " + result.message, "var(--cyber-warn)");
      return;
    }

    const data = result.data;
    const score = data.risk_score;
    const color = riskColor(score);

    // Status
    if (data.is_phishing) {
      setStatus("Threat Detected", "var(--cyber-danger)");
    } else {
      setStatus("System Clear", "var(--cyber-accent2)");
    }

    // Verdict tag
    if (data.verdict && data.verdict !== "Safe") {
      verdictEl.textContent = data.verdict;
    }

    // Metrics
    metricsRow.style.display = "grid";
    scoreNum.textContent = score;
    scoreNum.style.color = color;
    riskLevelVal.textContent = riskLabel(score);
    riskLevelVal.style.color = color;

    // Risk bar
    riskBarSection.style.display = "block";
    riskBar.style.setProperty("--bar-color", color);
    setTimeout(() => {
      riskBar.style.width = score + "%";
      barPct.textContent = score + "%";
      barPct.style.color = color;
    }, 80);

    // Summary
    summaryLine.style.display = "block";
    summaryLine.textContent = data.is_phishing
      ? "⚠ Phishing indicators detected on this page."
      : "✓ No threats found. This page appears safe.";

    // Reasons
    if (data.reasons && data.reasons.length > 0) {
      reasonsSection.classList.add("visible");
      data.reasons.forEach(reason => {
        const li = document.createElement("li");
        let icon = "⚠";
        if (reason.toLowerCase().includes("domain") || reason.toLowerCase().includes("trusted")) icon = "🌐";
        else if (reason.toLowerCase().includes("https")) icon = "🔒";
        li.textContent = icon + " " + reason;
        reasonsList.appendChild(li);
      });
    }

    // AI confidence
    if (typeof data.ml_confidence === "number") {
      aiConf.style.display = "flex";
      const pct = Math.round(data.ml_confidence * 100);
      aiConfVal.textContent = pct + "%";
      aiConfVal.style.color = pct > 70 ? "var(--cyber-danger)" : pct > 40 ? "var(--cyber-warn)" : "var(--cyber-accent2)";
    }

    // ── News Section ─────────────────────────────────
    const tabKey = `tab:${tab.id}`;
    const stored = await chrome.storage.local.get(tabKey);
    const newsData = stored[tabKey] && stored[tabKey].newsResult ? stored[tabKey].newsResult.data : null;

    if (newsData) {
      const newsScore = newsData.risk_score;
      const newsColor = newsData.is_fake_news ? "var(--cyber-warn)" : "var(--cyber-accent2)";

      newsContainer.innerHTML = `
        <div class="news-section">
          <div class="news-section-title">Content Integrity</div>
          <p class="news-status" style="color: ${newsColor};">
            ${newsData.is_fake_news ? "⚠ " : "✓ "}${newsData.verdict}
          </p>
          <p class="news-score">NEWS RISK SCORE: ${newsScore} / 100</p>
          ${newsData.reasons && newsData.reasons.length > 0
            ? `<ul id="news-reasons" style="list-style:none; display:flex; flex-direction:column; gap:5px; margin-top:4px;">
                ${newsData.reasons.map(r => `
                  <li style="font-family:'Rajdhani',sans-serif; font-size:12px; color:var(--cyber-text);
                    background:var(--cyber-card); border:1px solid var(--cyber-border);
                    border-radius:5px; padding:5px 10px; opacity:0.85;">${r}</li>
                `).join("")}
              </ul>`
            : ""}
        </div>
      `;
    }

  } catch (error) {
    setStatus("Backend Offline", "var(--cyber-danger)");
    statusBanner.style.display = "block";
    const errNote = document.createElement("p");
    errNote.style.cssText = "font-family:'Share Tech Mono',monospace; font-size:10px; color:var(--cyber-muted); margin-top:6px;";
    errNote.textContent = "Start the local API and reload.";
    statusBanner.appendChild(errNote);
  }

});