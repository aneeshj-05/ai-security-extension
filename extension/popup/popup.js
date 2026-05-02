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
      mlText.innerText = "ML Confidence: " + Math.round(data.ml_confidence * 100) + "%";
      document.body.appendChild(mlText);
    }

  } catch (error) {
    statusEl.innerText = "⚠️ Backend unavailable. Start the local API and try again.";
    statusEl.style.color = "red";
  }

});
