/**
 * AI Vehicle Damage Detection
 * Frontend Controller (Bilingual English/Kannada + LLM AI Assistant)
 */

let currentImageBase64 = null;
let currentPredictionResult = null;
let webcamStream = null;
let assessmentHistory = [];
let currentLang = "en"; // Default English

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    setupDragAndDrop();
    loadHistoryFromStorage();
    autoGenerateID();
    setupScrollListeners();
    initLanguage();
});

/* --------------------------------------------------------------------------
   Language Switcher & Internationalization (i18n)
   -------------------------------------------------------------------------- */
function initLanguage() {
    const savedLang = localStorage.getItem("app_lang") || "en";
    setLanguage(savedLang);
}

function setLanguage(lang) {
    if (!TRANSLATIONS[lang]) return;
    currentLang = lang;
    localStorage.setItem("app_lang", lang);

    // Update switcher button states
    const langEnBtn = document.getElementById("langEnBtn");
    const langKnBtn = document.getElementById("langKnBtn");
    if (langEnBtn && langKnBtn) {
        if (lang === "kn") {
            langKnBtn.classList.add("active");
            langEnBtn.classList.remove("active");
        } else {
            langEnBtn.classList.add("active");
            langKnBtn.classList.remove("active");
        }
    }

    // Update text for all elements with data-i18n
    const dict = TRANSLATIONS[lang];
    document.querySelectorAll("[data-i18n]").forEach(elem => {
        const key = elem.getAttribute("data-i18n");
        if (dict[key]) {
            elem.innerText = dict[key];
        }
    });

    // Update placeholders with data-i18n-ph
    document.querySelectorAll("[data-i18n-ph]").forEach(elem => {
        const key = elem.getAttribute("data-i18n-ph");
        if (dict[key]) {
            elem.placeholder = dict[key];
        }
    });

    // Update summary text if results are displayed
    if (currentPredictionResult) {
        renderBinaryResults(currentPredictionResult);
    }
}

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
        showToast(currentLang === 'kn' ? "ಚಿತ್ರವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಆಯ್ಕೆಮಾಡಲಾಗಿದೆ!" : "Image selected successfully!", "success");
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
        showToast(currentLang === 'kn' ? "ಕ್ಯಾಮೆರಾ ಸಕ್ರಿಯವಾಗಿದೆ" : "Camera active", "info");
    } catch (err) {
        console.error("Camera Access Error:", err);
        showToast("Unable to access webcam.", "error");
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
    showToast(currentLang === 'kn' ? "ಫೋಟೋ ಸೆರೆಹಿಡಿಯಲಾಗಿದೆ!" : "Photo captured!", "success");
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
    showToast(currentLang === 'kn' ? "ಚಿತ್ರವನ್ನು ತೆಗೆದುಹಾಕಲಾಗಿದೆ" : "Image removed", "info");
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
   Run Damage Assessment
   -------------------------------------------------------------------------- */
async function runDamageAssessment() {
    if (!currentImageBase64) {
        showToast(currentLang === 'kn' ? "ದಯವಿಟ್ಟು ಮೊದಲ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ!" : "Please select an image first!", "error");
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

        await new Promise(r => setTimeout(r, 450));

        loadingOverlay.style.display = "none";
        scannerBeamOverlay.classList.remove("active");

        if (data.status === "success") {
            currentPredictionResult = data;
            renderBinaryResults(data);
            showToast(currentLang === 'kn' ? "ತಪಾಸಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ!" : "Assessment Complete!", "success");
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
   Binary Results Renderer (Bilingual Support)
   -------------------------------------------------------------------------- */
function toggleImageView(viewType) {
    const origImg = document.getElementById("resultImage");
    const heatImg = document.getElementById("resultHeatmapImage");
    const pillOrig = document.getElementById("pillOrigBtn");
    const pillHeat = document.getElementById("pillHeatmapBtn");

    if (viewType === 'heatmap' && heatImg && heatImg.src) {
        if (origImg) origImg.style.display = "none";
        if (heatImg) heatImg.style.display = "block";
        if (pillOrig) pillOrig.classList.remove("active");
        if (pillHeat) pillHeat.classList.add("active");
    } else {
        if (origImg) origImg.style.display = "block";
        if (heatImg) heatImg.style.display = "none";
        if (pillOrig) pillOrig.classList.add("active");
        if (pillHeat) pillHeat.classList.remove("active");
    }
}

function renderBinaryResults(data) {
    const resultsSection = document.getElementById("resultsSection");
    const resultImage = document.getElementById("resultImage");
    const resultHeatmapImage = document.getElementById("resultHeatmapImage");
    const predictionStatusCard = document.getElementById("predictionStatusCard");
    const statusMainIcon = document.getElementById("statusMainIcon");
    const statusHeading = document.getElementById("statusHeading");
    const summaryText = document.getElementById("summaryText");

    if (resultImage && currentImageBase64) {
        resultImage.src = currentImageBase64;
    }
    if (resultHeatmapImage && data.heatmap_url) {
        resultHeatmapImage.src = data.heatmap_url;
    }
    toggleImageView('original');

    const isDamaged = data.prediction === "Damaged";
    const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;

    if (isDamaged) {
        predictionStatusCard.className = "result-card prediction-status-card damaged-mode";
        statusMainIcon.className = "fa-solid fa-circle-exclamation";
        statusHeading.innerText = dict.status_damaged;
        summaryText.innerText = dict.summary_damaged_text;
    } else {
        predictionStatusCard.className = "result-card prediction-status-card nodamage-mode";
        statusMainIcon.className = "fa-solid fa-circle-check";
        statusHeading.innerText = dict.status_nodamage;
        summaryText.innerText = dict.summary_nodamage_text;
    }

    // Category A: Populate Softmax Confidence & Probabilities (if elements exist)
    if (data.confidence_percentage !== undefined) {
        const confPct = document.getElementById("confidencePctVal");
        const damVal = document.getElementById("damagedProbVal");
        const whoVal = document.getElementById("wholeProbVal");
        const damFill = document.getElementById("damagedProbFill");
        const whoFill = document.getElementById("wholeProbFill");

        if (confPct) confPct.innerText = data.confidence_percentage;
        if (damVal) damVal.innerText = `${data.damaged_probability}%`;
        if (whoVal) whoVal.innerText = `${data.whole_probability}%`;
        if (damFill) damFill.style.width = `${data.damaged_probability}%`;
        if (whoFill) whoFill.style.width = `${data.whole_probability}%`;
    }

    // Category A: Quality & Duplicate Warning Chips
    if (data.quality) {
        document.getElementById("qualityScoreVal").innerText = data.quality.quality_score;
        if (data.quality.quality_warnings && data.quality.quality_warnings.length > 0) {
            showToast(`Quality Warning: ${data.quality.quality_warnings.join(" ")}`, "info");
        }
    }

    const dupChip = document.getElementById("duplicateWarningChip");
    if (dupChip) {
        dupChip.style.display = data.is_duplicate ? "inline-flex" : "none";
    }

    const uncertBox = document.getElementById("uncertaintyAlertBox");
    if (uncertBox) {
        uncertBox.style.display = data.is_uncertain ? "flex" : "none";
    }

    saveAssessmentToHistory(data);

    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* --------------------------------------------------------------------------
   Category B: Claim Readiness Modal Handler
   -------------------------------------------------------------------------- */
function openClaimReadinessModal() {
    document.getElementById("claimReadinessModal").style.display = "flex";
}

function closeClaimReadinessModal() {
    document.getElementById("claimReadinessModal").style.display = "none";
}

async function handleCalculateClaimReadiness(event) {
    event.preventDefault();
    const policyType = document.getElementById("crPolicyType").value;
    const licenseValid = document.getElementById("crLicenseStatus").value === "valid";
    const firFiled = document.getElementById("crFirStatus").value === "yes";
    const within30Days = document.getElementById("crTimeframe").value === "within_30";
    const isDamaged = currentPredictionResult ? currentPredictionResult.is_damaged : true;

    try {
        const response = await fetch("/api/evaluate_claim_readiness", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                policy_type: policyType,
                valid_license: licenseValid,
                fir_filed: firFiled,
                incident_within_30_days: within30Days,
                is_damaged: isDamaged
            })
        });

        const res = await response.json();
        if (res.status === "success") {
            const card = document.getElementById("readinessResultCard");
            card.style.display = "block";
            document.getElementById("readinessScoreVal").innerText = `${res.readiness_score}/100`;
            document.getElementById("readinessStatusTitle").innerText = res.status_text;
            document.getElementById("readinessRecommendation").innerText = res.recommendation;

            const badge = document.getElementById("readinessBadge");
            badge.className = `badge ${res.badge_class}`;
            badge.innerText = res.badge_class === 'success' ? 'Eligible' : (res.badge_class === 'warning' ? 'Review Needed' : 'Ineligible');

            const reasonsList = document.getElementById("readinessReasonsList");
            reasonsList.innerHTML = "";
            if (res.reasons && res.reasons.length > 0) {
                res.reasons.forEach(r => {
                    const li = document.createElement("li");
                    li.innerText = r;
                    reasonsList.appendChild(li);
                });
            }
        }
    } catch (err) {
        showToast("Failed to calculate readiness score.", "error");
    }
}

/* --------------------------------------------------------------------------
   AI Claims Assistant Chatbot Drawer & LLM API Integration
   -------------------------------------------------------------------------- */
function toggleChatDrawer() {
    const chatDrawer = document.getElementById("chatDrawerContainer");
    if (!chatDrawer) return;

    if (chatDrawer.style.display === "flex") {
        chatDrawer.style.display = "none";
    } else {
        chatDrawer.style.display = "flex";
        document.getElementById("chatInputText").focus();
    }
}

function sendFaqQuestion(faqId) {
    const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
    let questionText = "";
    if (faqId === 1) questionText = dict.faq_1.replace(/📋\s*/, '');
    else if (faqId === 2) questionText = dict.faq_2.replace(/⚠️\s*/, '');
    else if (faqId === 3) questionText = dict.faq_3.replace(/🤖\s*/, '');
    else if (faqId === 4) questionText = dict.faq_4.replace(/⏱️\s*/, '');

    if (questionText) {
        processSendChatMessage(questionText);
    }
}

function handleSendChat(e) {
    e.preventDefault();
    const chatInputText = document.getElementById("chatInputText");
    const message = chatInputText.value.trim();
    if (!message) return;

    chatInputText.value = "";
    processSendChatMessage(message);
}

async function processSendChatMessage(message) {
    const chatMessagesBody = document.getElementById("chatMessagesBody");
    const btnChatSend = document.getElementById("btnChatSend");

    // Append User Message Bubble
    appendChatMessage("user", message);

    // Append Loading Indicator Bubble
    const loadingBubbleId = "msg_loading_" + Date.now();
    appendChatMessage("bot", `<i class="fa-solid fa-spinner spinner"></i> ${currentLang === 'kn' ? 'AI ಉತ್ತರಿಸುತ್ತಿದೆ...' : 'AI is thinking...'}`, loadingBubbleId);

    btnChatSend.disabled = true;

    try {
        const vehicleCtx = currentPredictionResult ? currentPredictionResult.prediction : "";
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                language: currentLang,
                vehicle_context: vehicleCtx
            })
        });

        const data = await response.json();
        btnChatSend.disabled = false;

        // Remove loading bubble
        const loadingBubbleElem = document.getElementById(loadingBubbleId);
        if (loadingBubbleElem) loadingBubbleElem.remove();

        if (data.status === "success" && data.reply) {
            appendChatMessage("bot", data.reply);
        } else {
            appendChatMessage("bot", currentLang === 'kn' ? "ಕ್ಷಮಿಸಿ, ಮರುಪ್ರಯತ್ನಿಸಿ." : "Sorry, unable to get response. Please try again.");
        }

    } catch (err) {
        btnChatSend.disabled = false;
        const loadingBubbleElem = document.getElementById(loadingBubbleId);
        if (loadingBubbleElem) loadingBubbleElem.remove();
        console.error("Chat API Error:", err);
        appendChatMessage("bot", currentLang === 'kn' ? "ಸಂಪರ್ಕ ದೋಷ ಸಂಭವಿಸಿದೆ." : "Connection error to AI assistant.");
    }
}

function appendChatMessage(sender, text, elementId = null) {
    const chatMessagesBody = document.getElementById("chatMessagesBody");
    if (!chatMessagesBody) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-msg ${sender}`;
    if (elementId) msgDiv.id = elementId;

    const avatarHtml = sender === "bot" ? `<i class="fa-solid fa-robot bot-avatar"></i>` : "";
    msgDiv.innerHTML = `${avatarHtml}<div class="msg-bubble">${text}</div>`;

    chatMessagesBody.appendChild(msgDiv);
    chatMessagesBody.scrollTop = chatMessagesBody.scrollHeight;
}

/* --------------------------------------------------------------------------
   PDF Report Generator Modal, Download & Print Options
   -------------------------------------------------------------------------- */
let currentPdfAction = 'download';
let isSigDrawing = false;
let sigCanvas, sigCtx;

function initSignatureCanvas() {
    sigCanvas = document.getElementById("signatureCanvas");
    if (!sigCanvas) return;
    sigCtx = sigCanvas.getContext("2d");
    sigCtx.lineWidth = 2.5;
    sigCtx.lineCap = "round";
    sigCtx.strokeStyle = "#1E293B";

    function getPos(e) {
        const rect = sigCanvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }

    function startDraw(e) {
        isSigDrawing = true;
        const pos = getPos(e);
        sigCtx.beginPath();
        sigCtx.moveTo(pos.x, pos.y);
        const hint = document.getElementById("sigHint");
        if (hint) hint.style.display = "none";
    }

    function draw(e) {
        if (!isSigDrawing) return;
        if (e.preventDefault) e.preventDefault();
        const pos = getPos(e);
        sigCtx.lineTo(pos.x, pos.y);
        sigCtx.stroke();
    }

    function stopDraw() {
        isSigDrawing = false;
    }

    sigCanvas.onmousedown = startDraw;
    sigCanvas.onmousemove = draw;
    sigCanvas.onmouseup = stopDraw;
    sigCanvas.onmouseleave = stopDraw;

    sigCanvas.ontouchstart = startDraw;
    sigCanvas.ontouchmove = draw;
    sigCanvas.ontouchend = stopDraw;
}

function clearSignatureCanvas() {
    if (!sigCanvas || !sigCtx) return;
    sigCtx.clearRect(0, 0, sigCanvas.width, sigCanvas.height);
    const hint = document.getElementById("sigHint");
    if (hint) hint.style.display = "block";
}

function getSignatureData() {
    if (!sigCanvas || !sigCtx) return null;
    const pixelData = sigCtx.getImageData(0, 0, sigCanvas.width, sigCanvas.height).data;
    let hasContent = false;
    for (let i = 3; i < pixelData.length; i += 4) {
        if (pixelData[i] > 0) {
            hasContent = true;
            break;
        }
    }
    return hasContent ? sigCanvas.toDataURL("image/png") : null;
}

function openPdfModal(actionType = 'download') {
    currentPdfAction = actionType;
    autoGenerateID();
    const modal = document.getElementById("pdfInspectorModal");
    if (modal) modal.style.display = "flex";
    setTimeout(initSignatureCanvas, 100);
}

function closePdfModal() {
    const modal = document.getElementById("pdfInspectorModal");
    if (modal) modal.style.display = "none";
}

function autoGenerateID() {
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    const inspElem = document.getElementById("inspectionId");
    if (inspElem) inspElem.value = `INSP-2026-${randomNum}`;
}

function populatePrintableReportData(details = {}) {
    if (!currentPredictionResult) return;

    const now = new Date();
    const formattedDate = now.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
    const formattedTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const dateTimeStr = `${formattedDate} at ${formattedTime}`;

    const isDamaged = currentPredictionResult.prediction === "Damaged";

    // Date & Inspection IDs
    const rptDate = document.getElementById("rptDate");
    const rptInspectionId = document.getElementById("rptInspectionId");
    const rptInspectionIdCell = document.getElementById("rptInspectionIdCell");
    if (rptDate) rptDate.innerText = formattedDate;
    if (rptInspectionId) rptInspectionId.innerText = details.inspectionId || "INSP-2026";
    if (rptInspectionIdCell) rptInspectionIdCell.innerText = details.inspectionId || "INSP-2026";
    
    // Status Bar
    const statusBar = document.getElementById("rptStatusBar");
    const statusText = document.getElementById("rptStatusText");
    if (statusBar && statusText) {
        statusText.innerText = currentPredictionResult.prediction ? currentPredictionResult.prediction.toUpperCase() : "EVALUATED";
        statusBar.className = `report-status-bar ${isDamaged ? 'damaged' : 'nodamage'}`;
    }

    // Inspector metadata
    const rptInspectorName = document.getElementById("rptInspectorName");
    const rptVehicleNo = document.getElementById("rptVehicleNo");
    const rptPolicyNo = document.getElementById("rptPolicyNo");
    const rptTimestamp = document.getElementById("rptTimestamp");
    const rptFramework = document.getElementById("rptFramework");

    if (rptInspectorName) rptInspectorName.innerText = details.inspectorName || "N/A";
    if (rptVehicleNo) rptVehicleNo.innerText = details.vehicleNo || "N/A";
    if (rptPolicyNo) rptPolicyNo.innerText = details.policyNo || "N/A";
    if (rptTimestamp) rptTimestamp.innerText = dateTimeStr;
    if (rptFramework) rptFramework.innerText = currentPredictionResult.framework || "PyTorch CNN";

    // Image Quality Score
    const rptQualityScore = document.getElementById("rptQualityScore");
    if (rptQualityScore) rptQualityScore.innerText = `${currentPredictionResult.quality ? currentPredictionResult.quality.quality_score : 100}/100`;

    // Vehicle Photo
    const rptImg = document.getElementById("rptVehicleImage");
    const resultImg = document.getElementById("resultImage");
    const previewImg = document.getElementById("previewImage");
    const imgSrc = currentImageBase64 || (resultImg ? resultImg.src : (previewImg ? previewImg.src : ""));
    if (rptImg && imgSrc) {
        rptImg.src = imgSrc;
    }

    // AI Summary & Notes
    const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
    const summaryMsg = isDamaged ? dict.summary_damaged_text : dict.summary_nodamage_text;
    const rptSummaryText = document.getElementById("rptSummaryText");
    const rptInspectorNotes = document.getElementById("rptInspectorNotes");

    if (rptSummaryText) rptSummaryText.innerText = currentPredictionResult.summary || summaryMsg;
    if (rptInspectorNotes) rptInspectorNotes.innerText = details.notes || "No additional remarks.";

    // Footer info
    const rptFooterRef = document.getElementById("rptFooterRef");
    const rptFooterTime = document.getElementById("rptFooterTime");
    if (rptFooterRef) rptFooterRef.innerText = details.inspectionId || "REF-2026";
    if (rptFooterTime) rptFooterTime.innerText = dateTimeStr;
}

async function executeNativePrint() {
    const printableReport = document.getElementById("printableClaimReport");
    const rptImg = document.getElementById("rptVehicleImage");

    if (!printableReport) {
        showToast("Error: Printable report container missing", "error");
        return;
    }

    // Temporarily set display: block in screen DOM so browser layout engine computes geometry before printing
    printableReport.style.display = "block";

    // Ensure vehicle photo is fully loaded & decoded in DOM before opening print dialog
    if (rptImg && rptImg.src && rptImg.src !== window.location.href && !rptImg.src.endsWith("#")) {
        if (!rptImg.complete) {
            await new Promise((resolve) => {
                rptImg.onload = resolve;
                rptImg.onerror = resolve;
            });
        }
        if (rptImg.decode) {
            try {
                await rptImg.decode();
            } catch (e) {
                console.log("Image decode complete", e);
            }
        }
    }

    // Await animation frame + timeout to guarantee layout reflow for print styles
    await new Promise(r => requestAnimationFrame(() => setTimeout(r, 120)));

    window.print();

    // Reset style after print dialog closes
    setTimeout(() => {
        printableReport.style.display = "";
    }, 500);
}

async function handleGenerateReport(e, actionType = null) {
    if (e && e.preventDefault) e.preventDefault();
    const finalAction = actionType || currentPdfAction || 'download';

    if (!currentPredictionResult) {
        showToast("Please run damage assessment first!", "error");
        return;
    }

    const form = document.getElementById("inspectorForm");
    if (form && !form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const inspectorName = document.getElementById("inspectorName").value.trim();
    const vehicleNo = document.getElementById("vehicleNo").value.trim();
    const policyNo = document.getElementById("policyNo").value.trim();
    const inspectionId = document.getElementById("inspectionId").value.trim();
    const notes = document.getElementById("inspectionNotes").value.trim();

    // Populate Printable Report DOM Elements with entered claim metadata
    populatePrintableReportData({
        inspectorName,
        vehicleNo,
        policyNo,
        inspectionId,
        notes
    });

    if (finalAction === 'print') {
        // Close inspector details modal first
        closePdfModal();

        // Log record into session history
        saveAssessmentToHistory({
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            inspection_id: inspectionId,
            status: currentPredictionResult.prediction,
            report_url: "#"
        });

        // Trigger native browser print dialog after image decoding & DOM render
        showToast(currentLang === 'kn' ? "ಪ್ರಿಂಟ್ ಡೈಲಾಗ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ..." : "Opening Native Print Dialog...", "info");
        await executeNativePrint();
        return;
    }

    // IF finalAction === 'download': Execute existing PDF report file download
    const btnCompilePdf = document.getElementById("btnCompilePdf");
    const btnPrintPdf = document.getElementById("btnPrintPdf");

    if (btnCompilePdf) btnCompilePdf.disabled = true;
    if (btnPrintPdf) btnPrintPdf.disabled = true;

    if (btnCompilePdf) {
        btnCompilePdf.innerHTML = `<i class="fa-solid fa-spinner spinner"></i> ${currentLang === 'kn' ? 'ಸಂಸ್ಕರಿಸಲಾಗುತ್ತಿದೆ...' : 'Processing...'}`;
    }

    const payload = {
        inspector_name: inspectorName || "N/A",
        vehicle_no: vehicleNo || "N/A",
        policy_no: policyNo || "N/A",
        inspection_id: inspectionId || `INSP-${Date.now()}`,
        notes: notes || "No additional remarks.",
        image_id: currentPredictionResult.image_id,
        prediction: currentPredictionResult.prediction,
        summary: currentPredictionResult.summary,
        framework: currentPredictionResult.framework || "PyTorch 2.0",
        inference_time_ms: currentPredictionResult.inference_time_ms || 0,
        signature_data: getSignatureData()
    };

    try {
        const response = await fetch("/api/generate_report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (btnCompilePdf) {
            btnCompilePdf.disabled = false;
            btnCompilePdf.innerHTML = `<i class="fa-solid fa-file-pdf"></i> <span data-i18n="btn_download_pdf">Download PDF</span>`;
        }
        if (btnPrintPdf) {
            btnPrintPdf.disabled = false;
            btnPrintPdf.innerHTML = `<i class="fa-solid fa-print"></i> <span data-i18n="btn_print_report">Print Claim Report</span>`;
        }

        if (data.status === "success") {
            closePdfModal();

            saveAssessmentToHistory({
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                inspection_id: payload.inspection_id,
                status: currentPredictionResult.prediction,
                report_url: data.report_url
            });

            const downloadUrl = `${data.report_url}?download=1`;
            const link = document.createElement("a");
            link.href = downloadUrl;
            link.setAttribute("download", data.filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            showToast(currentLang === 'kn' ? "PDF ವರದಿ ಡೌನ್‌ಲೋಡ್ ಆಗಿದೆ!" : "PDF Report Downloaded Successfully!", "success");
        } else {
            showToast("PDF Error: " + (data.message || "Failed to generate PDF"), "error");
        }
    } catch (err) {
        if (btnCompilePdf) {
            btnCompilePdf.disabled = false;
            btnCompilePdf.innerHTML = `<i class="fa-solid fa-file-pdf"></i> Download PDF`;
        }
        if (btnPrintPdf) {
            btnPrintPdf.disabled = false;
            btnPrintPdf.innerHTML = `<i class="fa-solid fa-print"></i> Print Claim Report`;
        }
        console.error("PDF API Error:", err);
        showToast("Error connecting to PDF generator.", "error");
    }
}

async function printAssessmentResult() {
    if (!currentPredictionResult) {
        showToast("Please run an assessment first!", "error");
        return;
    }

    const inspectorName = document.getElementById("inspectorName") ? document.getElementById("inspectorName").value.trim() : "";
    const vehicleNo = document.getElementById("vehicleNo") ? document.getElementById("vehicleNo").value.trim() : "";
    const policyNo = document.getElementById("policyNo") ? document.getElementById("policyNo").value.trim() : "";
    const inspectionId = document.getElementById("inspectionId") ? document.getElementById("inspectionId").value.trim() : "";
    const notes = document.getElementById("inspectionNotes") ? document.getElementById("inspectionNotes").value.trim() : "";

    populatePrintableReportData({ inspectorName, vehicleNo, policyNo, inspectionId, notes });
    await executeNativePrint();
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
    const formattedRecord = {
        timestamp: record.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        inspection_id: record.inspection_id || `INSP-${(record.image_id || 'LOCAL').slice(-6).toUpperCase()}`,
        status: record.prediction || record.status || "Unknown",
        confidence: record.confidence_percentage ? `${record.confidence_percentage}%` : "N/A",
        report_url: record.report_url || "#"
    };
    
    // Prevent duplicate entries by inspection_id
    if (!assessmentHistory.some(h => h.inspection_id === formattedRecord.inspection_id)) {
        assessmentHistory.unshift(formattedRecord);
        if (assessmentHistory.length > 20) assessmentHistory.pop();
        localStorage.setItem("vehicle_assessment_history_binary", JSON.stringify(assessmentHistory));
        renderHistoryTable();
    }
}

function renderHistoryTable() {
    const tableBody = document.getElementById("historyTableBody");
    const historyCount = document.getElementById("historyCount");

    if (!tableBody) return;

    if (assessmentHistory.length === 0) {
        const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
        tableBody.innerHTML = `
            <tr id="emptyHistoryRow">
                <td colspan="4" class="empty-table-cell">
                    <i class="fa-solid fa-folder-open"></i>
                    <p>${dict.history_empty}</p>
                </td>
            </tr>
        `;
        if (historyCount) historyCount.innerText = "0 Records";
        return;
    }

    if (historyCount) historyCount.innerText = `${assessmentHistory.length} Records`;

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
    showToast(currentLang === 'kn' ? "ಇತಿಹಾಸವನ್ನು ಅಳಿಸಲಾಗಿದೆ" : "History cleared", "info");
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
