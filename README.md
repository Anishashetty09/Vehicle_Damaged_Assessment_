# AI Vehicle Damage Assessment & Insurance Inspection System 🚘💥🛡️

An end-to-end production-quality AI web application built for automated vehicle damage classification and instant insurance claim report generation using a **fine-tuned PyTorch ResNet-18 CNN model**, **Flask backend**, and a **modern, responsive Dashboard frontend**.

---

## 🌟 Key System Features

- **PyTorch ResNet-18 Deep Learning Engine**:
  - Classifies vehicle images into **Damaged** (`00-damage`) or **Whole** (`01-whole`).
  - Preprocesses images using TorchVision transforms (`Resize`, `CenterCrop`, `ToTensor`, `Normalize` with ImageNet mean/std).
  - Performs inference in evaluation mode (`model.eval()`, `torch.no_grad()`) delivering sub-millisecond execution times.
  - Computes class probability distribution, confidence score (%), AI severity index (1-10), and estimated repair cost range.

- **Dual Image Acquisition (Upload & Live Webcam)**:
  - **Drag-and-Drop Dropzone** with file validation for JPG, PNG, WEBP.
  - **Integrated Live Webcam Stream** with real-time video preview, snapshot capture, and camera controls.
  - **Interactive AI Radar Scanner** animated overlay during classification.

- **Automated ReportLab PDF Report Generation**:
  - Compiles an official **Vehicle Inspection & Claim Approval Certificate**.
  - Embeds the captured vehicle snapshot, inspector metadata (Inspector Name, Policy No, Vehicle Registration, Inspection ID), AI classification badge, confidence meter, claim recommendation, and authorized signature block.

- **Session History & Inspection Logs**:
  - Real-time session history drawer tracking past scans with direct PDF download links.

---

## 📁 Modular Directory Architecture

```text
sic_vehicle_anti/
├── app.py                      # Flask Server & REST API endpoints (/api/predict, /api/generate_report)
├── train_model.py              # Script to train/save PyTorch model state_dict (.pth)
├── requirements.txt            # Project Python package requirements
├── README.md                   # Capstone System Documentation
├── models/
│   ├── vehicle_damage_model.py # PyTorch ResNet-18 CNN architecture definition
│   └── vehicle_damage_model.pth# Trained PyTorch checkpoint state_dict
├── utils/
│   ├── model_handler.py        # Model loading, eval mode & torch.no_grad() inference handler
│   ├── image_processor.py      # Pillow & TorchVision preprocessing transforms
│   └── pdf_generator.py        # ReportLab PDF Inspection Report Builder
├── templates/
│   └── index.html              # Main HTML5 Single Page Application Dashboard
├── static/
│   ├── css/
│   │   └── style.css           # Custom Glassmorphism & Cyberpunk Dark UI Theme
│   └── js/
│       └── main.js             # Camera capture, Drag & Drop, API requests & UI controller
├── uploads/                    # Server storage for uploaded/captured vehicle photos
└── reports/                    # Server storage for generated PDF inspection reports
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites & Environment Setup
Ensure Python 3.9+ is installed. Install required Python packages:

```bash
pip install -r requirements.txt
```

### 2. PyTorch Model Checkpoint Generation
Run `train_model.py` to initialize and export the model state_dict:

```bash
python train_model.py
```

### 3. Launch Flask Web Application
Start the development server:

```bash
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔌 REST API Specifications

### 1. Predict Vehicle Damage
- **Endpoint**: `POST /api/predict`
- **Request Body**:
  ```json
  {
    "image_data": "data:image/jpeg;base64,..."
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "prediction": "Damaged",
    "confidence": 98.4,
    "probabilities": { "Damaged": 98.4, "Whole": 1.6 },
    "severity_score": 8.5,
    "repair_estimate": "$3,825 - $6,375",
    "inference_time_ms": 3.45,
    "framework": "PyTorch 2.13.0+cpu",
    "recommendation": "CLAIM APPROVED - Immediate Body Shop Repair Required."
  }
  ```

### 2. Generate PDF Inspection Report
- **Endpoint**: `POST /api/generate_report`
- **Request Body**: Inspector metadata + prediction details
- **Response**: PDF download URL (`/download_report/report_INSP-2026-8801.pdf`).

---

## 🎓 Engineering Capstone Project Highlights

1. **Production-Ready Code**: Strict separation of concerns (Models, Handlers, Controllers, Views, Utilities).
2. **Deep Learning Best Practices**: Use of `torch.no_grad()`, proper `eval()` mode switching, and exact TorchVision ImageNet normalization matching training pipeline.
3. **Robust UI/UX Design**: Modern dark mode aesthetics with responsive layouts, real-time micro-animations, camera webcam canvas handling, and seamless PDF download workflow.
