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
    const summaryText = document.getElementById("summary-text");
    const fileChip = document.getElementById("file-chip");
    const statusBadge = document.getElementById("status-badge");
    const videoPreview = document.getElementById("video-preview");
    const videoPlaceholder = document.getElementById("video-placeholder");

    const loadingMessages = [
        "Uploading and running multimodal pipeline...",
        "Extracting speech, emotions, and body cues...",
        "Fusing signals into a unified timeline..."
    ];

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
        if (file) {
            handleFileSelect(file);
        }
    });

    fileInput.addEventListener("change", () => {
        const file = fileInput.files?.[0];
        if (file) {
            handleFileSelect(file);
        }
    });

    processBtn.addEventListener("click", async () => {
        if (!selectedFile) {
            return;
        }

        timelineBody.innerHTML = "";
        resultsSection.classList.add("hidden");
        loading.classList.remove("hidden");
        processBtn.disabled = true;
        setStatus("Running", "running");
        startLoadingTicker();

        if (videoPreview.src) {
            videoPreview.play().catch(() => {
                // If autoplay is blocked, the user can still press play manually.
            });
        }

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("/api/process", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Processing failed");
            }

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

        if (currentVideoUrl) {
            URL.revokeObjectURL(currentVideoUrl);
        }
        currentVideoUrl = URL.createObjectURL(file);
        videoPreview.src = currentVideoUrl;
        videoPreview.classList.remove("hidden");
        videoPlaceholder.classList.add("hidden");
    }

    function renderResults(data) {
        const timeline = Array.isArray(data.timeline) ? data.timeline : [];
        const emotions = timeline.map((item) => item.emotion).filter(Boolean);
        const behaviors = timeline.map((item) => item.behavior).filter(Boolean);

        metricSegments.textContent = String(timeline.length);
        metricEmotions.textContent = mostCommon(emotions) || "-";
        metricBehaviors.textContent = mostCommon(behaviors) || "-";
        summaryText.textContent = buildSummary(timeline);

        timeline.forEach((item) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${formatTimestamp(item.timestamp)}</td>
                <td>${escapeHtml(item.speech || "Silent")}</td>
                <td>${escapeHtml(item.emotion || "unknown")}</td>
                <td>${escapeHtml(item.behavior || "unknown")}</td>
                <td>${escapeHtml(item.insight || "No notable multimodal event")}</td>
            `;
            timelineBody.appendChild(row);
        });

        resultsSection.classList.remove("hidden");
    }

    function buildSummary(timeline) {
        if (!timeline.length) {
            return "No timeline events were generated for this run.";
        }

        const uncertainSpeech = timeline.filter((item) => !item.speech || item.speech.toLowerCase().includes("unclear")).length;
        const dominantEmotion = mostCommon(timeline.map((item) => item.emotion).filter(Boolean)) || "neutral";
        const dominantBehavior = mostCommon(timeline.map((item) => item.behavior).filter(Boolean)) || "stable";

        return `The dominant visible emotion was ${dominantEmotion}. Body behavior appeared mostly ${dominantBehavior}. ${uncertainSpeech > 0 ? `${uncertainSpeech} segment(s) contained weak or unclear speech.` : `Speech was captured for most visible segments.`}`;
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
        if (!values.length) {
            return "";
        }
        const counts = new Map();
        values.forEach((value) => counts.set(value, (counts.get(value) || 0) + 1));
        return [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
    }

    function formatTimestamp(value) {
        const numeric = Number(value || 0);
        return `${numeric.toFixed(1)}s`;
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }
});
