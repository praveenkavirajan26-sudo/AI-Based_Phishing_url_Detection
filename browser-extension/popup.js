document.addEventListener('DOMContentLoaded', function() {
    const scanBtn = document.getElementById('scan-btn');
    const urlDisplay = document.getElementById('url-display');
    const resultDiv = document.getElementById('result');
    const loader = document.getElementById('loader');

    let currentUrl = "";

    // Query active tab URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        if(tabs && tabs.length > 0) {
            currentUrl = tabs[0].url;
            urlDisplay.textContent = currentUrl;
        }
    });

    scanBtn.addEventListener('click', async () => {
        if(!currentUrl) return;
        
        scanBtn.style.display = 'none';
        loader.style.display = 'block';
        resultDiv.style.display = 'none';

        try {
            const response = await fetch("http://localhost:8000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: currentUrl })
            });
            
            if(!response.ok) throw new Error("API Connection Error");
            
            const data = await response.json();
            
            resultDiv.style.display = 'block';
            let intelHtml = "";
            if (data.threat_intel) {
                const isSafe = data.threat_intel.safe;
                intelHtml = `<div class="intel">
                    <strong>Intel:</strong> ${data.threat_intel.source}<br>
                    Status:  ${isSafe ? 'Clean' : '⚠️ THREAT FOUND'}
                </div>`;
            }

            if (data.is_phishing) {
                resultDiv.className = 'danger';
                resultDiv.innerHTML = `<strong>DANGER: PHISHING</strong><br>
                                       Confidence: ${data.confidence_score}%<br>
                                       Risk: ${data.risk_score}%
                                       ${intelHtml}`;
            } else {
                resultDiv.className = 'safe';
                resultDiv.innerHTML = `<strong>SAFE PAGE</strong><br>
                                       Confidence: ${data.confidence_score}%<br>
                                       Risk: ${data.risk_score}%
                                       ${intelHtml}`;
            }
        } catch (error) {
            resultDiv.style.display = 'block';
            resultDiv.className = 'danger';
            resultDiv.innerText = "Error: Could not reach backend API at localhost:8000";
        } finally {
            loader.style.display = 'none';
            scanBtn.style.display = 'block';
            scanBtn.innerText = "Scan Again";
        }
    });
});
