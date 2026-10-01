/* ══════════════════════════════════════
   GLOBAL REVIEW ID + CHARTS
══════════════════════════════════════ */
let currentReviewId = null;
let confidenceChart, predictionChart, sentimentChart;


/* ══════════════════════════════════════
   CSRF HELPER
══════════════════════════════════════ */
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1] ?? '';
}


/* ══════════════════════════════════════
   SHOW RESULT
══════════════════════════════════════ */
function showResult(resultEl, { isGenuine, confidence, error }) {
    if (error) {
        resultEl.innerHTML = `❌ ${error}`;
        return;
    }

    const icon = isGenuine ? '✅' : '⚠️';
    const label = isGenuine ? 'Genuine Review' : 'Fake Review';

    resultEl.innerHTML = `
        <strong>${icon} ${label}</strong><br>
        Confidence: ${confidence.toFixed(1)}%
    `;
}


/* ══════════════════════════════════════
   SHOW SENTIMENT
══════════════════════════════════════ */
function showSentimentResult(resultEl, { sentiment, error }) {
    if (error) {
        resultEl.innerHTML = `❌ ${error}`;
        return;
    }

    resultEl.innerHTML = `<strong>Sentiment: ${sentiment}</strong>`;
}


/* ══════════════════════════════════════
   PREDICT REVIEW + CHARTS
══════════════════════════════════════ */
async function predictReview() {
    const text = document.getElementById('reviewText').value.trim();
    const resultEl = document.getElementById('result');

    if (!text) {
        resultEl.innerHTML = "⚠️ Enter review";
        return;
    }

    resultEl.innerHTML = "⏳ Analysing...";

    try {
        const res = await fetch('/pred_rev/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ text })
        });

        const data = await res.json();

        currentReviewId = data.id;

        const rawConf = data.confidence ?? data.confidance ?? 0;
        const isGenuine = data.prediction === 'GENUINE';

        showResult(resultEl, {
            isGenuine,
            confidence: rawConf * 100
        });

        /* 🔥 SHOW GRAPH SECTION */
        document.getElementById("predictionCharts").style.display = "block";

        /* 🔥 DESTROY OLD */
        if (confidenceChart) confidenceChart.destroy();
        if (predictionChart) predictionChart.destroy();

        /* 🔥 CONFIDENCE */
        confidenceChart = new Chart(
            document.getElementById('confidenceChartSingle'),
            {
                type: 'bar',
                data: {
                    labels: ['Confidence'],
                    datasets: [{
                        data: [rawConf * 100],
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    }
                }
            }
        );

        /* 🔥 FAKE VS GENUINE */
        predictionChart = new Chart(
            document.getElementById('predictionChartSingle'),
            {
                type: 'doughnut',
                data: {
                    labels: ['Fake', 'Genuine'],
                    datasets: [{
                        data: isGenuine ? [0, 100] : [100, 0],
                    }]
                }
            }
        );

    } catch {
        resultEl.innerHTML = "❌ Error";
    }
}


/* ══════════════════════════════════════
   SENTIMENT + CHART
══════════════════════════════════════ */
async function analyseSentiment() {
    const text = document.getElementById('reviewText').value.trim();
    const resultEl = document.getElementById('result');

    if (!text) {
        resultEl.innerHTML = "⚠️ Enter text";
        return;
    }

    if (!currentReviewId) {
        resultEl.innerHTML = "⚠️ Run detection first";
        return;
    }

    resultEl.innerHTML = "⏳ Analysing sentiment...";

    try {
        const res = await fetch('/pred_senti/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({
                text,
                review_id: currentReviewId
            })
        });

        const data = await res.json();

        showSentimentResult(resultEl, {
            sentiment: data.sentiments
        });

        /* 🔥 DESTROY OLD */
        if (sentimentChart) sentimentChart.destroy();

        const isPositive = data.sentiments === 'positive';

        /* 🔥 SENTIMENT CHART */
        sentimentChart = new Chart(
            document.getElementById('sentimentChartSingle'),
            {
                type: 'bar',
                data: {
                    labels: ['Positive', 'Negative'],
                    datasets: [{
                        data: isPositive ? [100, 0] : [0, 100],
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    }
                }
            }
        );

    } catch {
        resultEl.innerHTML = "❌ Error";
    }
}