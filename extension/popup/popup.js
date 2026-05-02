document.addEventListener("DOMContentLoaded", async () => {
  let statusEl = document.getElementById("status");
  let scoreEl = document.getElementById("score");
  let verdictEl = document.getElementById("verdict");
  let reasonsList = document.getElementById("reasons");

  statusEl.innerText = "🔍 Analyzing...";
  reasonsList.innerHTML = "";

  try {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    let url = tab.url;

    if (!url || !url.startsWith("http")) {
      statusEl.innerText = "ℹ️ Please navigate to a standard web page to analyze it.";
      statusEl.style.color = "gray";
      document.getElementById("score").innerText = "";
      document.getElementById("verdict").innerText = "";
      return;
    }

    const result = await globalThis.AiSecurityApi.analyzeUrl(url);

    if (!result.ok) {
      statusEl.innerText = "⚠️ " + result.message;
      statusEl.style.color = "orange";
      return;
    }

    const data = result.data;

    if (data.is_phishing) {
      statusEl.innerText = "🔴 Phishing Detected";
      statusEl.style.color = "red";
    } else {
      statusEl.innerText = "🟢 Safe Website";
      statusEl.style.color = "green";
    }

    scoreEl.innerText = "Risk Score: " + data.risk_score + " / 100";

    if (data.risk_score > 70) {
      scoreEl.style.color = "red";
    } else if (data.risk_score > 40) {
      scoreEl.style.color = "orange";
    } else {
      scoreEl.style.color = "green";
    }

    verdictEl.innerText = data.verdict !== "Safe" ? data.verdict : "";

    let summary = document.createElement("p");
    summary.style.fontWeight = "bold";

    summary.innerText = data.is_phishing
      ? "⚠️ This website shows phishing indicators."
      : "✅ This website appears safe.";

    verdictEl.after(summary);

    let riskLevel;

    if (data.risk_score > 70) {
      riskLevel = "High Risk";
    } else if (data.risk_score > 40) {
      riskLevel = "Moderate Risk";
    } else {
      riskLevel = "Low Risk";
    }

    let riskText = document.createElement("p");
    riskText.innerText = "Risk Level: " + riskLevel;

    scoreEl.after(riskText);

    if (data.reasons && data.reasons.length > 0) {
      document.getElementById("reasons-header").style.display = "block";
      data.reasons.forEach(reason => {
        let li = document.createElement("li");

        if (reason.toLowerCase().includes("domain") || reason.toLowerCase().includes("trusted")) {
          li.innerText = "🌐 " + reason;
        } else if (reason.toLowerCase().includes("https")) {
          li.innerText = "🔒 " + reason;
        } else {
          li.innerText = "⚠️ " + reason;
        }

        reasonsList.appendChild(li);
      });
    }

    if (typeof data.ml_confidence === "number") {
      let mlText = document.createElement("p");
      mlText.innerText = "Phishing AI Confidence: " + Math.round(data.ml_confidence * 100) + "%";
      mlText.style.fontSize = "11px";
      mlText.style.marginTop = "10px";
      mlText.style.color = "#6b7280";
      document.body.appendChild(mlText);
    }

    // --- News Integrity Check ---
    const tabKey = `tab:${tab.id}`;
    const stored = await chrome.storage.local.get(tabKey);
    const newsData = stored[tabKey] && stored[tabKey].newsResult ? stored[tabKey].newsResult.data : null;

    if (newsData) {
      const hr = document.createElement("hr");
      hr.style.margin = "15px 0";
      hr.style.border = "none";
      hr.style.borderTop = "1px solid #e5e7eb";
      document.body.appendChild(hr);

      const newsHeader = document.createElement("h4");
      newsHeader.innerText = "Content Integrity";
      newsHeader.style.margin = "0 0 8px 0";
      document.body.appendChild(newsHeader);

      const newsStatus = document.createElement("p");
      newsStatus.innerText = newsData.is_fake_news ? "⚠️ " + newsData.verdict : "✅ " + newsData.verdict;
      newsStatus.style.color = newsData.is_fake_news ? "#f59e0b" : "#16a34a";
      newsStatus.style.fontWeight = "bold";
      document.body.appendChild(newsStatus);

      const newsScore = document.createElement("p");
      newsScore.innerText = "News Risk Score: " + newsData.risk_score + " / 100";
      newsScore.style.fontSize = "12px";
      document.body.appendChild(newsScore);

      if (newsData.reasons && newsData.reasons.length > 0) {
          const newsReasons = document.createElement("ul");
          newsReasons.style.paddingLeft = "18px";
          newsReasons.style.fontSize = "12px";
          newsReasons.style.color = "#4b5563";
          newsData.reasons.forEach(r => {
              const li = document.createElement("li");
              li.innerText = r;
              newsReasons.appendChild(li);
          });
          document.body.appendChild(newsReasons);
      }
    }

  } catch (error) {
    statusEl.innerText = "⚠️ Backend unavailable. Start the local API and try again.";
    statusEl.style.color = "red";
  }

});
