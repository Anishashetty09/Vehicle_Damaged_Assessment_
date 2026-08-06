/**
 * AI Vehicle Damage Detection
 * Frontend Controller (Strict Binary Classification Mode)
 */

let currentImageBase64 = null;
let currentPredictionResult = null;
let webcamStream = null;
let assessmentHistory = [];

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    setupDragAndDrop();
    loadHistoryFromStorage();
    autoGenerateID();
    setupScrollListeners();
});

/* --------------------------------------------------------------------------
   Theme Switcher & LocalStorage Persistence
   -------------------------------------------------------------------------- */
function initTheme() {
    const savedTheme = localStorage.getItem("app_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("app_theme", newTheme);
    updateThemeIcon(newTheme);
    showToast(`Switched to ${newTheme.toUpperCase()} mode`, "info");
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById("themeIcon");
    if (themeIcon) {
        themeIcon.className = theme === "dark" ? "fa-solid fa-moon" : "fa-solid fa-sun";
    }
}

/* --------------------------------------------------------------------------
   Navigation & Section Router
   -------------------------------------------------------------------------- */
function navigateTo(sectionId) {
    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === `#${sectionId}`) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });

    const navMenu = document.getElementById("navMenu");
    if (navMenu) navMenu.classList.remove("open");

    let targetElem = null;
    if (sectionId === "home") targetElem = document.getElementById("homeSection");
    else if (sectionId === "assessment") targetElem = document.getElementById("assessmentSection");
    else if (sectionId === "results") {
        targetElem = document.getElementById("resultsSection");
        targetElem.style.display = "block";
    }
    else if (sectionId === "history") targetElem = document.getElementById("historySection");

    if (targetElem) {
        targetElem.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

function toggleMobileNav() {
    const navMenu = document.getElementById("navMenu");
    if (navMenu) navMenu.classList.toggle("open");
}

/* --------------------------------------------------------------------------
   Tab Navigation Handler (Upload vs Camera)
   -------------------------------------------------------------------------- */
function switchAcquisitionTab(tabName) {
    const uploadBody = document.getElementById("uploadTabBody");
    const cameraBody = document.getElementById("cameraTabBody");
    const tabUploadBtn = document.getElementById("tabUploadBtn");
    const tabCameraBtn = document.getElementById("tabCameraBtn");

    if (tabName === "upload") {
        uploadBody.classList.add("active");
        cameraBody.classList.remove("active");
        tabUploadBtn.classList.add("active");
        tabCameraBtn.classList.remove("active");
        stopCamera();
    } else if (tabName === "camera") {
        cameraBody.classList.add("active");
        uploadBody.classList.remove("active");
        tabCameraBtn.classList.add("active");
        tabUploadBtn.classList.remove("active");
    }
}

/* --------------------------------------------------------------------------
   Drag and Drop & File Selection
   -------------------------------------------------------------------------- */
function triggerFileInput() {
    document.getElementById("fileInput").click();
}

function triggerNewUpload() {
    resetAssessment();
    setTimeout(() => {
        triggerFileInput();
    }, 100);
}

function setupDragAndDrop() {
    const dropzone = document.getElementById("dropzone");
    if (!dropzone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', handleDrop, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
        processSelectedFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files && files.length > 0) {
        processSelectedFile(files[0]);
    }
}

function processSelectedFile(file) {
    if (!file.type.match('image.*')) {
        showToast("Please select a valid image file (JPG, PNG, WEBP).", "error");
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showToast("File size exceeds 16MB limit.", "error");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        currentImageBase64 = e.target.result;
        displayImageStagePreview(currentImageBase64, file.name);
        showToast("Image selected successfully!", "success");
    };
    reader.readAsDataURL(file);
}

/* --------------------------------------------------------------------------
   Live Camera Stream Controller
   -------------------------------------------------------------------------- */
async function startCamera() {
    const video = document.getElementById("webcamVideo");
    const placeholder = document.getElementById("cameraPlaceholder");
    const startBtn = document.getElementById("startCamBtn");
    const captureBtn = document.getElementById("captureCamBtn");
    const stopBtn = document.getElementById("stopCamBtn");

    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        video.srcObject = webcamStream;
        video.style.display = "block";
        placeholder.style.display = "none";

        startBtn.disabled = true;
        captureBtn.disabled = false;
        stopBtn.disabled = false;
        showToast("Camera active", "info");
    } catch (err) {
        console.error("Camera Access Error:", err);
        showToast("Unable to access webcam. Check camera permissions.", "error");
    }
}

function captureSnapshot() {
    const video = document.getElementById("webcamVideo");
    const canvas = document.getElementById("snapshotCanvas");
    const context = canvas.getContext("2d");

    if (!webcamStream) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    currentImageBase64 = canvas.toDataURL("image/jpeg");
    displayImageStagePreview(currentImageBase64, "webcam_snapshot.jpg");
    stopCamera();
    showToast("Photo captured!", "success");
}

function stopCamera() {
    const video = document.getElementById("webcamVideo");
    const placeholder = document.getElementById("cameraPlaceholder");
    const startBtn = document.getElementById("startCamBtn");
    const captureBtn = document.getElementById("captureCamBtn");
    const stopBtn = document.getElementById("stopCamBtn");

    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }

    if (video) video.style.display = "none";
    if (placeholder) placeholder.style.display = "flex";
    if (startBtn) startBtn.disabled = false;
    if (captureBtn) captureBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = true;
}

/* --------------------------------------------------------------------------
   Stage Preview & Image Reset
   -------------------------------------------------------------------------- */
function displayImageStagePreview(src, filename) {
    const previewStageCard = document.getElementById("previewStageCard");
    const previewImage = document.getElementById("previewImage");
    const previewFilename = document.getElementById("previewFilename");

    previewImage.src = src;
    previewFilename.innerHTML = `<i class="fa-solid fa-file-image"></i> ${filename}`;
    previewStageCard.style.display = "flex";
    previewStageCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function promptRemoveImage() {
    document.getElementById("confirmDeleteModal").style.display = "flex";
}

function closeConfirmDeleteModal() {
    document.getElementById("confirmDeleteModal").style.display = "none";
}

function confirmRemoveImage() {
    closeConfirmDeleteModal();
    resetAssessment();
    showToast("Image removed", "info");
}

function resetAssessment() {
    currentImageBase64 = null;
    currentPredictionResult = null;
    document.getElementById("fileInput").value = "";
    document.getElementById("previewStageCard").style.display = "none";
    document.getElementById("resultsSection").style.display = "none";
    navigateTo('assessment');
}

/* --------------------------------------------------------------------------
   Run Damage Assessment (Strict Binary AI Model Evaluation)
   -------------------------------------------------------------------------- */
async function runDamageAssessment() {
    if (!currentImageBase64) {
        showToast("Please upload an image or capture a photo first!", "error");
        return;
    }

    const loadingOverlay = document.getElementById("loadingOverlay");
    const scannerBeamOverlay = document.getElementById("scannerBeamOverlay");
    
    loadingOverlay.style.display = "flex";
    scannerBeamOverlay.classList.add("active");

    updateProgressStep("stepUpload", "done");
    updateProgressStep("stepAI", "active");

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image_data: currentImageBase64 })
        });

        updateProgressStep("stepAI", "done");
        updateProgressStep("stepDetect", "active");

        const data = await response.json();

        updateProgressStep("stepDetect", "done");
        updateProgressStep("stepReport", "active");

        await new Promise(r => setTimeout(r, 450)); // smooth step transition

        loadingOverlay.style.display = "none";
        scannerBeamOverlay.classList.remove("active");

        if (data.status === "success") {
            currentPredictionResult = data;
            renderBinaryResults(data);
            showToast("Assessment Complete!", "success");
        } else {
            showToast("Assessment Error: " + (data.message || "Unknown error"), "error");
        }
    } catch (err) {
        loadingOverlay.style.display = "none";
        scannerBeamOverlay.classList.remove("active");
        console.error("API Request Failure:", err);
        showToast("Failed to connect to backend server.", "error");
    }
}

function updateProgressStep(stepId, state) {
    const stepElem = document.getElementById(stepId);
    if (!stepElem) return;
    
    if (state === "active") {
        stepElem.className = "p-step active";
        stepElem.querySelector("i").className = "fa-solid fa-spinner spinner";
    } else if (state === "done") {
        stepElem.className = "p-step done";
        stepElem.querySelector("i").className = "fa-solid fa-circle-check";
    }
}

/* --------------------------------------------------------------------------
   Strict Binary Results Renderer
   -------------------------------------------------------------------------- */
function renderBinaryResults(data) {
    const resultsSection = document.getElementById("resultsSection");
    const resultImage = document.getElementById("resultImage");
    const predictionStatusCard = document.getElementById("predictionStatusCard");
    const statusIconCircle = document.getElementById("statusIconCircle");
    const statusMainIcon = document.getElementById("statusMainIcon");
    const statusHeading = document.getElementById("statusHeading");
    const summaryText = document.getElementById("summaryText");

    // Display Uploaded Image beside result card
    if (resultImage && currentImageBase64) {
        resultImage.src = currentImageBase64;
    }

    // Determine binary prediction (Damaged vs No Damage Detected)
    const isDamaged = data.prediction === "Damaged";

    if (isDamaged) {
        predictionStatusCard.className = "result-card prediction-status-card damaged-mode";
        statusMainIcon.className = "fa-solid fa-circle-exclamation";
        statusHeading.innerText = "Damaged";
        summaryText.innerText = "The AI model detected visible signs that indicate the vehicle is damaged. This prediction is based on image analysis.";
    } else {
        predictionStatusCard.className = "result-card prediction-status-card nodamage-mode";
        statusMainIcon.className = "fa-solid fa-circle-check";
        statusHeading.innerText = "No Damage Detected";
        summaryText.innerText = "The AI model did not detect visible damage in the uploaded image.";
    }

    // Reveal results page & smooth scroll
    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* --------------------------------------------------------------------------
   PDF Report Generator Modal & Download
   -------------------------------------------------------------------------- */
function openPdfModal() {
    autoGenerateID();
    document.getElementById("pdfInspectorModal").style.display = "flex";
}

function closePdfModal() {
    document.getElementById("pdfInspectorModal").style.display = "none";
}

function autoGenerateID() {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const inspElem = document.getElementById("inspectionId");
    if (inspElem) inspElem.value = `INSP-2026-${randomNum}`;
}

async function handleGenerateReport(e) {
    e.preventDefault();

    if (!currentPredictionResult) {
        showToast("Please run damage assessment first!", "error");
        return;
    }

    const inspectorName = document.getElementById("inspectorName").value.trim();
    const vehicleNo = document.getElementById("vehicleNo").value.trim();
    const policyNo = document.getElementById("policyNo").value.trim();
    const inspectionId = document.getElementById("inspectionId").value.trim();
    const notes = document.getElementById("inspectionNotes").value.trim();

    const btnCompilePdf = document.getElementById("btnCompilePdf");
    btnCompilePdf.disabled = true;
    btnCompilePdf.innerHTML = `<i class="fa-solid fa-spinner spinner"></i> Compiling PDF...`;

    const payload = {
        inspector_name: inspectorName,
        vehicle_no: vehicleNo,
        policy_no: policyNo,
        inspection_id: inspectionId,
        notes: notes,
        image_id: currentPredictionResult.image_id,
        prediction: currentPredictionResult.prediction,
        summary: currentPredictionResult.summary,
        framework: currentPredictionResult.framework,
        inference_time_ms: currentPredictionResult.inference_time_ms
    };

    try {
        const response = await fetch("/api/generate_report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        btnCompilePdf.disabled = false;
        btnCompilePdf.innerHTML = `<i class="fa-solid fa-file-pdf"></i> Download PDF`;

        if (data.status === "success") {
            closePdfModal();
            const downloadAnchor = document.createElement("a");
            downloadAnchor.href = data.report_url;
            downloadAnchor.target = "_blank";
            downloadAnchor.download = data.filename;
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            document.body.removeChild(downloadAnchor);

            // Save to local storage history
            saveAssessmentToHistory({
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                inspection_id: inspectionId,
                status: currentPredictionResult.prediction,
                report_url: data.report_url
            });

            showToast("PDF Report Downloaded!", "success");
        } else {
            showToast("PDF Error: " + (data.message || "Failed to generate PDF"), "error");
        }
    } catch (err) {
        btnCompilePdf.disabled = false;
        btnCompilePdf.innerHTML = `<i class="fa-solid fa-file-pdf"></i> Download PDF`;
        console.error("PDF API Error:", err);
        showToast("Error connecting to PDF generator.", "error");
    }
}

/* --------------------------------------------------------------------------
   Local Storage History Manager
   -------------------------------------------------------------------------- */
function loadHistoryFromStorage() {
    const stored = localStorage.getItem("vehicle_assessment_history_binary");
    if (stored) {
        try {
            assessmentHistory = JSON.parse(stored);
            renderHistoryTable();
        } catch (e) {
            assessmentHistory = [];
        }
    }
}

function saveAssessmentToHistory(record) {
    assessmentHistory.unshift(record);
    if (assessmentHistory.length > 20) assessmentHistory.pop();
    localStorage.setItem("vehicle_assessment_history_binary", JSON.stringify(assessmentHistory));
    renderHistoryTable();
}

function renderHistoryTable() {
    const tableBody = document.getElementById("historyTableBody");
    const historyCount = document.getElementById("historyCount");

    if (!tableBody) return;

    if (assessmentHistory.length === 0) {
        tableBody.innerHTML = `
            <tr id="emptyHistoryRow">
                <td colspan="4" class="empty-table-cell">
                    <i class="fa-solid fa-folder-open"></i>
                    <p>No records saved yet. Complete an assessment to see history here.</p>
                </td>
            </tr>
        `;
        if (historyCount) historyCount.innerText = "0 Assessment Records";
        return;
    }

    if (historyCount) historyCount.innerText = `${assessmentHistory.length} Assessment Records`;

    tableBody.innerHTML = assessmentHistory.map(rec => `
        <tr>
            <td>${rec.timestamp}</td>
            <td><strong>${rec.inspection_id}</strong></td>
            <td><span class="badge ${rec.status === 'Damaged' ? 'pytorch-badge' : 'status-badge-online'}">${rec.status}</span></td>
            <td>
                <a href="${rec.report_url}" target="_blank" class="btn-small text-success"><i class="fa-solid fa-download"></i> PDF</a>
            </td>
        </tr>
    `).join('');
}

function clearSessionHistory() {
    assessmentHistory = [];
    localStorage.removeItem("vehicle_assessment_history_binary");
    renderHistoryTable();
    showToast("History cleared", "info");
}

/* --------------------------------------------------------------------------
   Interactive Modals, Toasts & Scroll
   -------------------------------------------------------------------------- */
function openLightbox() {
    const previewImage = document.getElementById("previewImage");
    const lightboxModal = document.getElementById("lightboxModal");
    const lightboxImage = document.getElementById("lightboxImage");

    if (previewImage && lightboxModal && lightboxImage) {
        lightboxImage.src = previewImage.src;
        lightboxModal.style.display = "flex";
    }
}

function closeLightbox() {
    const lightboxModal = document.getElementById("lightboxModal");
    if (lightboxModal) lightboxModal.style.display = "none";
}

function showToast(message, type = "info") {
    const toastContainer = document.getElementById("toastContainer");
    if (!toastContainer) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    let icon = "fa-circle-info";
    if (type === "success") icon = "fa-circle-check";
    if (type === "error") icon = "fa-triangle-exclamation";

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(40px)";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function setupScrollListeners() {
    const fabTopBtn = document.getElementById("fabTopBtn");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 300) {
            if (fabTopBtn) fabTopBtn.style.display = "flex";
        } else {
            if (fabTopBtn) fabTopBtn.style.display = "none";
        }
    });
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}
