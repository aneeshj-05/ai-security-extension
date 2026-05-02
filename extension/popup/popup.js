document.addEventListener("DOMContentLoaded", async () => {

  
  let statusEl = document.getElementById("status");
  let scoreEl = document.getElementById("score");
  let verdictEl = document.getElementById("verdict");
  let reasonsList = document.getElementById("reasons");

  statusEl.innerText = "🔍 Analyzing...";

  try {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    let url = tab.url;

    const response = await fetch("http://127.0.0.1:8000/api/v1/analyze-url", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: url })
    });

    const data = await response.json();

    
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

    
    reasonsList.innerHTML = "";

    data.reasons.forEach(reason => {
      let li = document.createElement("li");

      if (reason.toLowerCase().includes("domain")) {
        li.innerText = "🌐 " + reason;
      } else if (reason.toLowerCase().includes("https")) {
        li.innerText = "🔒 " + reason;
      } else {
        li.innerText = "⚠️ " + reason;
      }

      reasonsList.appendChild(li);
    });

    
    if (data.ml_confidence !== undefined) {
      let mlText = document.createElement("p");
      mlText.innerText = "ML Confidence: " + Math.round(data.ml_confidence * 100) + "%";
      document.body.appendChild(mlText);
    }

  } catch (error) {
    statusEl.innerText = "⚠️ Error connecting to backend";
  }

});