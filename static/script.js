document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const themeToggle = document.getElementById("theme-toggle");
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const processBtn = document.getElementById("process-btn");
    const loading = document.getElementById("loading");
    const loadingMessage = document.getElementById("loading-message");
    const resultsSection = document.getElementById("results-section");
    const timelineBody = document.getElementById("timeline-body");
    const metricSegments = document.getElementById("metric-segments");
    const metricEmotions = document.getElementById("metric-emotions");
    const metricBehaviors = document.getElementById("metric-behaviors");
    const metricIntegrity = document.getElementById("metric-integrity");
    const summaryText = document.getElementById("summary-text");
    const fileChip = document.getElementById("file-chip");
    const statusBadge = document.getElementById("status-badge");
    const videoPreview = document.getElementById("video-preview");
    const videoPlaceholder = document.getElementById("video-placeholder");
    const emotionChart = document.getElementById("emotion-chart");
    const emotionChartEmpty = document.getElementById("emotion-chart-empty");
    const chartLegend = document.getElementById("chart-legend");

    const loadingMessages = [
        "Uploading and running multimodal pipeline...",
        "Extracting speech, emotions, and body cues...",
        "Fusing signals into a unified timeline..."
    ];

    const emotionPalette = {
        happy: "#1ecb74",
        sad: "#4da3ff",
        angry: "#ff6b3d",
        fear: "#b084ff",
        surprise: "#ffd84d",
        neutral: "#f1f5f9",
        disgust: "#14c4b8",
        no_face_detected: "#64748b",
        unknown: "#94a3b8"
    };

    let selectedFile = null;
    let currentVideoUrl = null;
    let loadingTicker = null;

    applyStoredTheme();

    themeToggle.addEventListener("click", () => {
        const nextTheme = body.dataset.theme === "dark" ? "light" : "dark";
        setTheme(nextTheme);
    });

    dropZone.addEventListener("click", () => fileInput.click());
    dropZone.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            fileInput.click();
        }
    });

    dropZone.addEventListener("dragover", (event) => {
        event.preventDefault();
        dropZone.classList.add("active");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("active");
    });

    dropZone.addEventListener("drop", (event) => {
        event.preventDefault();
        dropZone.classList.remove("active");
        const file = event.dataTransfer.files?.[0];
        if (file) handleFileSelect(file);
    });

    fileInput.addEventListener("change", () => {
        const file = fileInput.files?.[0];
        if (file) handleFileSelect(file);
    });

    processBtn.addEventListener("click", async () => {
        if (!selectedFile) return;

        timelineBody.innerHTML = "";
        resultsSection.classList.add("hidden");
        resetEmotionChart();
        metricIntegrity.textContent = "-";
        loading.classList.remove("hidden");
        processBtn.disabled = true;
        setStatus("Running", "running");
        startLoadingTicker();

        if (videoPreview.src) {
            videoPreview.play().catch(() => {});
        }

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("/api/process", { method: "POST", body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Processing failed");
            localStorage.setItem("latestAnalysis", JSON.stringify(data));
            renderResults(data);
            setStatus("Complete", "done");
        } catch (error) {
            summaryText.textContent = error.message;
            setStatus("Failed", "error");
            alert("Error: " + error.message);
        } finally {
            stopLoadingTicker();
            loading.classList.add("hidden");
            processBtn.disabled = false;
        }
    });

    function handleFileSelect(file) {
        selectedFile = file;
        processBtn.disabled = false;
        fileChip.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB`;
        dropZone.querySelector(".drop-title").textContent = "Video selected";
        dropZone.querySelector(".drop-copy").textContent = "You can press Start Analysis and keep watching the video here.";
        summaryText.textContent = "Ready to run analysis on the selected video.";
        setStatus("Ready", "idle");

        if (currentVideoUrl) URL.revokeObjectURL(currentVideoUrl);
        currentVideoUrl = URL.createObjectURL(file);
        videoPreview.src = currentVideoUrl;
        videoPreview.classList.remove("hidden");
        videoPlaceholder.classList.add("hidden");
    }

    function renderResults(data) {
        const timeline = Array.isArray(data.timeline) ? data.timeline : [];
        const emotions = timeline.map((item) => item.emotion).filter(Boolean);
        const behaviors = timeline.map((item) => item.behavior).filter(Boolean);
        const integrityScore = calculateIntegrityScore(data);

        metricSegments.textContent = String(timeline.length);
        metricEmotions.textContent = mostCommon(emotions) || "-";
        metricBehaviors.textContent = mostCommon(behaviors) || "-";
        metricIntegrity.textContent = `${integrityScore}%`;
        summaryText.textContent = buildSummary(timeline, metricIntegrity.textContent);

        timeline.forEach((item) => {
            const row = document.createElement("tr");
            row.innerHTML = `<td>${formatTimestamp(item.timestamp)}</td><td>${escapeHtml(item.speech || "Silent")}</td><td>${escapeHtml(item.emotion || "unknown")}</td><td>${escapeHtml(item.behavior || "unknown")}</td><td>${escapeHtml(item.insight || "No notable multimodal event")}</td>`;
            timelineBody.appendChild(row);
        });

        renderEmotionChart(Array.isArray(data.emotion) ? data.emotion : []);
        resultsSection.classList.remove("hidden");
    }

    function calculateIntegrityScore(data) {
        const timeline = Array.isArray(data.timeline) ? data.timeline : [];
        const speech = Array.isArray(data.speech) ? data.speech : [];
        const emotion = Array.isArray(data.emotion) ? data.emotion : [];
        const behavior = Array.isArray(data.behavior) ? data.behavior : [];
        if (!timeline.length) return 0;
        const speechCoverage = coverage(speech.filter((item) => item.text && item.text !== "unclear speech").length, timeline.length);
        const avgSpeechConfidence = average(speech.map((item) => Number(item.confidence || 0)));
        const avgEmotionConfidence = average(emotion.map((item) => Number(item.confidence || 0)));
        const behaviorCoverage = coverage(behavior.filter((item) => item.behavior && item.behavior !== "unknown").length, timeline.length);
        const noFaceRatio = fraction(emotion.filter((item) => (item.emotion || "") === "no_face_detected").length, emotion.length);
        const rawScore = ((avgSpeechConfidence * 0.3) + (speechCoverage * 0.2) + (avgEmotionConfidence * 0.25) + (behaviorCoverage * 0.15) + ((1 - noFaceRatio) * 0.1)) * 100;
        return clampPercent(rawScore);
    }

    function renderEmotionChart(emotionData) {
        resetEmotionChart();
        if (!emotionData.length) return;
        const filtered = emotionData.filter((item) => typeof item.timestamp === "number" && typeof item.confidence === "number").sort((a, b) => a.timestamp - b.timestamp);
        if (!filtered.length) return;
        const uniqueEmotions = [...new Set(filtered.map((item) => item.emotion || "unknown"))];
        buildLegend(uniqueEmotions);
        const width = 1040;
        const height = 320;
        const margin = { top: 18, right: 24, bottom: 44, left: 52 };
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;
        const maxTime = Math.max(...filtered.map((item) => item.timestamp), 1);
        const yTicks = [0, 0.25, 0.5, 0.75, 1];
        const xScale = (value) => margin.left + (value / maxTime) * chartWidth;
        const yScale = (value) => margin.top + ((1 - value) * chartHeight);
        const lines = uniqueEmotions.map((emotion) => {
            const series = filtered.filter((item) => (item.emotion || "unknown") === emotion);
            const color = getEmotionColor(emotion);
            const path = series.map((item, index) => `${index === 0 ? "M" : "L"} ${xScale(item.timestamp).toFixed(2)} ${yScale(item.confidence).toFixed(2)}`).join(" ");
            const points = series.map((item) => {
                const x = xScale(item.timestamp);
                const y = yScale(item.confidence);
                return `<circle class="series-point" cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="4" fill="${color}"></circle><circle class="point-hitbox" cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="12" data-emotion="${escapeAttribute(emotion)}" data-confidence="${item.confidence.toFixed(3)}" data-timestamp="${item.timestamp.toFixed(1)}"></circle>`;
            }).join("");
            return `<path class="series-line" d="${path}" stroke="${color}"></path>${points}`;
        }).join("");
        const xTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const value = ratio * maxTime;
            const x = xScale(value);
            return `<line class="grid-line" x1="${x.toFixed(2)}" y1="${margin.top}" x2="${x.toFixed(2)}" y2="${(margin.top + chartHeight).toFixed(2)}"></line><text class="tick-label" x="${x.toFixed(2)}" y="${(height - 12).toFixed(2)}" text-anchor="middle">${value.toFixed(1)}s</text>`;
        }).join("");
        const yGrid = yTicks.map((value) => {
            const y = yScale(value);
            return `<line class="grid-line" x1="${margin.left}" y1="${y.toFixed(2)}" x2="${(margin.left + chartWidth).toFixed(2)}" y2="${y.toFixed(2)}"></line><text class="tick-label" x="${(margin.left - 10).toFixed(2)}" y="${(y + 4).toFixed(2)}" text-anchor="end">${value.toFixed(2)}</text>`;
        }).join("");
        emotionChart.innerHTML = `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Emotion confidence over time">${yGrid}${xTicks}<line class="axis-line" x1="${margin.left}" y1="${(margin.top + chartHeight).toFixed(2)}" x2="${(margin.left + chartWidth).toFixed(2)}" y2="${(margin.top + chartHeight).toFixed(2)}"></line><line class="axis-line" x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${(margin.top + chartHeight).toFixed(2)}"></line>${lines}<text class="axis-label" x="${(margin.left + chartWidth / 2).toFixed(2)}" y="${(height - 2).toFixed(2)}" text-anchor="middle">Time</text><text class="axis-label" x="16" y="${(margin.top + chartHeight / 2).toFixed(2)}" text-anchor="middle" transform="rotate(-90 16 ${((margin.top + chartHeight / 2).toFixed(2))})">Confidence</text></svg><div id="chart-tooltip" class="chart-tooltip hidden"></div>`;
        attachTooltipHandlers();
        emotionChart.classList.remove("hidden");
        emotionChartEmpty.classList.add("hidden");
    }

    function attachTooltipHandlers() {
        const tooltip = document.getElementById("chart-tooltip");
        const targets = emotionChart.querySelectorAll(".point-hitbox");
        targets.forEach((target) => {
            target.addEventListener("mouseenter", (event) => {
                tooltip.innerHTML = `<strong>${escapeHtml(event.target.dataset.emotion)}</strong><br>Confidence: ${event.target.dataset.confidence}<br>Time: ${event.target.dataset.timestamp}s`;
                tooltip.classList.remove("hidden");
            });
            target.addEventListener("mousemove", (event) => {
                const bounds = emotionChart.getBoundingClientRect();
                tooltip.style.left = `${event.clientX - bounds.left + 14}px`;
                tooltip.style.top = `${event.clientY - bounds.top - 8}px`;
            });
            target.addEventListener("mouseleave", () => tooltip.classList.add("hidden"));
        });
    }

    function buildLegend(emotions) {
        chartLegend.innerHTML = emotions.map((emotion) => `<span class="legend-item"><span class="legend-swatch" style="background:${getEmotionColor(emotion)}"></span><span>${escapeHtml(emotion)}</span></span>`).join("");
    }

    function resetEmotionChart() {
        emotionChart.innerHTML = "";
        chartLegend.innerHTML = "";
        emotionChart.classList.add("hidden");
        emotionChartEmpty.classList.remove("hidden");
    }

    function buildSummary(timeline, integrityLabel) {
        if (!timeline.length) return "No timeline events were generated for this run.";
        const uncertainSpeech = timeline.filter((item) => !item.speech || item.speech.toLowerCase().includes("unclear")).length;
        const dominantEmotion = mostCommon(timeline.map((item) => item.emotion).filter(Boolean)) || "neutral";
        const dominantBehavior = mostCommon(timeline.map((item) => item.behavior).filter(Boolean)) || "stable";
        return `The dominant visible emotion was ${dominantEmotion}. Body behavior appeared mostly ${dominantBehavior}. Integrity score is ${integrityLabel}. ${uncertainSpeech > 0 ? `${uncertainSpeech} segment(s) contained weak or unclear speech.` : `Speech was captured for most visible segments.`}`;
    }

    function setStatus(label, stateClass) {
        statusBadge.textContent = label;
        statusBadge.className = `status-badge ${stateClass}`;
    }

    function startLoadingTicker() {
        let index = 0;
        loadingMessage.textContent = loadingMessages[index];
        loadingTicker = window.setInterval(() => {
            index = (index + 1) % loadingMessages.length;
            loadingMessage.textContent = loadingMessages[index];
        }, 2200);
    }

    function stopLoadingTicker() {
        if (loadingTicker) {
            window.clearInterval(loadingTicker);
            loadingTicker = null;
        }
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

    function mostCommon(values) {
        if (!values.length) return "";
        const counts = new Map();
        values.forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
        return [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
    }

    function average(values) {
        if (!values.length) return 0;
        return values.reduce((sum, value) => sum + Number(value || 0), 0) / values.length;
    }

    function coverage(count, total) {
        if (!total) return 0;
        return Math.min(1, count / total);
    }

    function fraction(count, total) {
        if (!total) return 1;
        return count / total;
    }

    function clampPercent(value) {
        return Math.max(0, Math.min(100, Math.round(value)));
    }

    function formatTimestamp(value) {
        const numeric = Number(value || 0);
        return `${numeric.toFixed(1)}s`;
    }

    function getEmotionColor(emotion) {
        return emotionPalette[emotion] || emotionPalette.unknown;
    }

    function escapeHtml(value) {
        return String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function escapeAttribute(value) {
        return escapeHtml(value).replace(/`/g, "&#96;");
    }
});
