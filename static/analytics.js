document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const themeToggle = document.getElementById("theme-toggle");
    const analyticsIntegrity = document.getElementById("analytics-integrity");
    const integrityCopy = document.getElementById("integrity-copy");
    const integrityRingSvg = document.getElementById("integrity-ring-svg");
    const modelBars = document.getElementById("model-bars");
    const emotionDonut = document.getElementById("emotion-donut");
    const donutLegend = document.getElementById("donut-legend");
    const donutTotal = document.getElementById("donut-total");
    const emotionBreakdown = document.getElementById("emotion-breakdown");
    const fusionScoreCard = document.getElementById("fusion-score-card");
    const bestModelCard = document.getElementById("best-model-card");
    const averageAccuracyCard = document.getElementById("average-accuracy-card");

    const benchmark = {
        fusionScore: 88,
        models: [
            { key: "speech", label: "Speech Model", accuracy: 91 },
            { key: "emotion", label: "Emotion Model", accuracy: 84 },
            { key: "behavior", label: "Behavior Model", accuracy: 79 },
            { key: "fusion", label: "Fusion Engine", accuracy: 88 }
        ],
        emotions: [
            { emotion: "neutral", count: 34 },
            { emotion: "happy", count: 22 },
            { emotion: "surprise", count: 15 },
            { emotion: "sad", count: 11 },
            { emotion: "angry", count: 9 },
            { emotion: "fear", count: 6 },
            { emotion: "disgust", count: 3 }
        ]
    };

    const emotionPalette = {
        happy: "#1ecb74",
        sad: "#4da3ff",
        angry: "#ff6b3d",
        fear: "#b084ff",
        surprise: "#ffd84d",
        neutral: "#f1f5f9",
        disgust: "#14c4b8",
        unknown: "#94a3b8"
    };

    const modelPalette = {
        speech: "linear-gradient(90deg, #60a5fa 0%, #2563eb 100%)",
        emotion: "linear-gradient(90deg, #f97316 0%, #ef4444 100%)",
        behavior: "linear-gradient(90deg, #2dd4bf 0%, #0f766e 100%)",
        fusion: "linear-gradient(90deg, #c084fc 0%, #7c3aed 100%)"
    };

    applyStoredTheme();
    renderBenchmark();

    themeToggle.addEventListener("click", () => {
        const nextTheme = body.dataset.theme === "dark" ? "light" : "dark";
        setTheme(nextTheme);
    });

    function renderBenchmark() {
        analyticsIntegrity.textContent = `${benchmark.fusionScore}%`;
        fusionScoreCard.textContent = `${benchmark.fusionScore}%`;
        const bestModel = [...benchmark.models].sort((a, b) => b.accuracy - a.accuracy)[0];
        bestModelCard.textContent = bestModel ? bestModel.label : "-";
        averageAccuracyCard.textContent = `${Math.round(benchmark.models.reduce((sum, item) => sum + item.accuracy, 0) / benchmark.models.length)}%`;
        integrityCopy.textContent = "Fusion score is computed from previous validation runs and reflects how well the speech, emotion, and behavior models align together.";
        renderIntegrityRing(benchmark.fusionScore);
        renderModelBars(benchmark.models);
        renderEmotionDonut(benchmark.emotions);
    }

    function renderIntegrityRing(score) {
        const radius = 62;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference * (1 - (score / 100));
        const color = score >= 85 ? "#1ecb74" : score >= 70 ? "#ffd84d" : "#ff6b3d";
        integrityRingSvg.innerHTML = `<circle class="ring-track" cx="90" cy="90" r="${radius}"></circle><circle class="ring-progress" cx="90" cy="90" r="${radius}" stroke="${color}" stroke-dasharray="${circumference.toFixed(2)}" stroke-dashoffset="${offset.toFixed(2)}"></circle>`;
    }

    function renderModelBars(models) {
        modelBars.innerHTML = models.map((item) => `
            <div class="model-row">
                <div class="model-label">${item.label}</div>
                <div class="model-track"><div class="model-fill" style="width:${item.accuracy}%; background:${modelPalette[item.key]}"></div></div>
                <div class="model-value">${item.accuracy}%</div>
            </div>
        `).join("");
    }

    function renderEmotionDonut(emotions) {
        const total = emotions.reduce((sum, item) => sum + item.count, 0);
        donutTotal.textContent = String(total);
        const radius = 78;
        const circumference = 2 * Math.PI * radius;
        let offset = 0;

        const segments = emotions.map((item) => {
            const ratio = item.count / total;
            const dash = circumference * ratio;
            const segment = `<circle class="donut-segment" cx="120" cy="120" r="${radius}" stroke="${getEmotionColor(item.emotion)}" stroke-dasharray="${dash.toFixed(2)} ${(circumference - dash).toFixed(2)}" stroke-dashoffset="${(-offset).toFixed(2)}"></circle>`;
            offset += dash;
            return segment;
        }).join("");

        emotionDonut.innerHTML = `<circle class="ring-track" cx="120" cy="120" r="${radius}"></circle>${segments}`;
        donutLegend.innerHTML = emotions.map((item) => `<span class="legend-item"><span class="legend-swatch" style="background:${getEmotionColor(item.emotion)}"></span><span>${escapeHtml(item.emotion)}</span></span>`).join("");
        emotionBreakdown.innerHTML = emotions.map((item) => {
            const percent = Math.round((item.count / total) * 100);
            return `<div class="breakdown-row"><span class="breakdown-swatch" style="background:${getEmotionColor(item.emotion)}"></span><span class="breakdown-label">${escapeHtml(item.emotion)}</span><span class="breakdown-meta">${item.count}</span><span class="breakdown-meta">${percent}%</span></div>`;
        }).join("");
    }

    function setTheme(theme) {
        body.dataset.theme = theme;
        localStorage.setItem("mvis-theme", theme);
        themeToggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }

    function applyStoredTheme() {
        const storedTheme = localStorage.getItem("mvis-theme");
        setTheme(storedTheme === "light" ? "light" : "dark");
    }

    function getEmotionColor(emotion) {
        return emotionPalette[emotion] || emotionPalette.unknown;
    }

    function escapeHtml(value) {
        return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#39;");
    }
});
