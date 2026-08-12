import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import uuid
import datetime
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from utils.image_processor import decode_base64_image, process_image, check_image_quality, compute_image_hash
from utils.model_handler import get_model_handler
from utils.pdf_generator import generate_pdf_report
from utils.llm_handler import get_llm_handler

# Initialize Flask application
app = Flask(__name__, static_folder="static", template_folder="templates")

# Configure directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
HASH_STORE_FILE = os.path.join(UPLOAD_FOLDER, "processed_hashes.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload limit

# In-memory Hash Cache
KNOWN_HASHES = {}
if os.path.exists(HASH_STORE_FILE):
    try:
        with open(HASH_STORE_FILE, "r") as f:
            KNOWN_HASHES = json.load(f)
    except Exception:
        KNOWN_HASHES = {}

def save_hash_cache():
    try:
        with open(HASH_STORE_FILE, "w") as f:
            json.dump(KNOWN_HASHES, f)
    except Exception as e:
        print(f"[WARNING] Failed to save hash store: {e}")

# Pre-load PyTorch Model Handler & LLM Handler Singletons
model_handler = get_model_handler()
llm_handler = get_llm_handler()

@app.route("/")
def index():
    """Renders the main Application Dashboard."""
    return render_template("index.html")

@app.route("/api/predict", methods=["POST"])
def predict():
    """
    API Endpoint for Vehicle Damage Classification.
    Executes PyTorch model inference with quality checks & perceptual hash duplicate detection.
    """
    try:
        data = request.get_json(silent=True)
        pil_image = None

        if data and "image_data" in data:
            base64_str = data["image_data"]
            pil_image = decode_base64_image(base64_str)
        elif "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                from PIL import Image
                pil_image = Image.open(file.stream)

        if pil_image is None:
            return jsonify({
                "status": "error",
                "message": "No valid image payload provided."
            }), 400

        # Ensure RGB format
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # 1. Quality & Blur Analysis
        quality_analysis = check_image_quality(pil_image)

        # 2. Perceptual Content Hash & Duplicate Check
        img_hash = compute_image_hash(pil_image)
        is_duplicate = img_hash in KNOWN_HASHES
        previous_inspection = KNOWN_HASHES.get(img_hash)

        # Save snapshot into uploads/ directory
        image_id = f"img_{uuid.uuid4().hex[:10]}"
        image_filename = f"{image_id}.jpg"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        pil_image.save(image_path, "JPEG", quality=92)

        # Record hash
        KNOWN_HASHES[img_hash] = image_id
        save_hash_cache()

        # Apply PyTorch Model Inference with TTA & Grad-CAM Heatmap
        result = model_handler.predict(pil_image)
        
        # Save Heatmap snapshot into uploads/ directory
        heatmap_pil = result.pop("heatmap_pil", None)
        heatmap_filename = f"heatmap_{image_id}.jpg"
        if heatmap_pil:
            heatmap_path = os.path.join(app.config["UPLOAD_FOLDER"], heatmap_filename)
            heatmap_pil.save(heatmap_path, "JPEG", quality=92)
            result["heatmap_url"] = f"/uploads/{heatmap_filename}"
        else:
            result["heatmap_url"] = f"/uploads/{image_filename}"

        # Append metadata & quality analytics
        result["status"] = "success"
        result["image_id"] = image_id
        result["image_url"] = f"/uploads/{image_filename}"
        result["quality"] = quality_analysis
        result["is_duplicate"] = is_duplicate
        result["duplicate_ref"] = previous_inspection if is_duplicate else None

        return jsonify(result), 200

    except Exception as e:
        print(f"[ERROR] Inference Exception: {e}")
        return jsonify({
            "status": "error",
            "message": f"Inference processing failed: {str(e)}"
        }), 500

@app.route("/api/evaluate_claim_readiness", methods=["POST"])
def evaluate_claim_readiness():
    """
    API Endpoint for Deterministic Claim Readiness & Policy Eligibility Assessment.
    """
    try:
        data = request.get_json() or {}
        policy_type = data.get("policy_type", "Comprehensive")
        fir_filed = data.get("fir_filed", False)
        valid_license = data.get("valid_license", True)
        is_damaged = data.get("is_damaged", True)
        incident_within_30_days = data.get("incident_within_30_days", True)

        readiness_score = 100
        reasons = []

        if not valid_license:
            readiness_score -= 50
            reasons.append("Driver's license is reported invalid or expired.")

        if not is_damaged:
            readiness_score -= 40
            reasons.append("AI model detected no visible damage on the vehicle.")

        if policy_type == "Third Party Only":
            readiness_score -= 30
            reasons.append("Third-party policies do not cover own-vehicle damage.")

        if not incident_within_30_days:
            readiness_score -= 20
            reasons.append("Claim delayed beyond standard 30-day reporting period.")

        if not fir_filed and is_damaged:
            reasons.append("FIR copy recommended for major accident claims.")

        if readiness_score >= 80:
            status_text = "Eligible for Fast-Track Claim Submission"
            recommendation = "All primary eligibility criteria met. Submit report directly to insurer."
            badge_class = "success"
        elif readiness_score >= 50:
            status_text = "Conditional Approval - Manual Review Needed"
            recommendation = "Claim requires manual loss adjuster verification due to missing documentation or policy constraints."
            badge_class = "warning"
        else:
            status_text = "High Risk / Potentially Ineligible"
            recommendation = "Claim may be rejected under standard policy terms. Review policy terms."
            badge_class = "danger"

        # Estimated Repair Cost Tier
        if is_damaged:
            if readiness_score >= 80:
                estimated_cost = "₹15,000 - ₹35,000 (Covered under Insurance)"
            elif readiness_score >= 50:
                estimated_cost = "₹35,000 - ₹75,000 (Subject to Loss Adjuster Verification)"
            else:
                estimated_cost = "₹75,000+ (High Severity / Major Collision Claim)"
        else:
            estimated_cost = "₹0 (No visible damage detected)"

        return jsonify({
            "status": "success",
            "readiness_score": readiness_score,
            "status_text": status_text,
            "recommendation": recommendation,
            "reasons": reasons,
            "badge_class": badge_class,
            "estimated_cost": estimated_cost
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    API Endpoint for AI Claims Assistant LLM Chatbot.
    Accepts user question, language (en/kn), and vehicle inspection context.
    """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"status": "error", "message": "No prompt message provided."}), 400

        user_message = data.get("message", "").strip()
        language = data.get("language", "en")
        vehicle_context = data.get("vehicle_context", "")

        reply = llm_handler.chat_response(user_message, language=language, vehicle_context=vehicle_context)

        return jsonify({
            "status": "success",
            "reply": reply,
            "language": language
        }), 200

    except Exception as e:
        print(f"[ERROR] LLM Chat Exception: {e}")
        return jsonify({
            "status": "error",
            "message": f"LLM assistant failed to process request: {str(e)}"
        }), 500

@app.route("/api/generate_report", methods=["POST"])
def generate_report():
    """
    API Endpoint for PDF Inspection Report Generation.
    Accepts inspector details, prediction results, digital signature, and generates ReportLab PDF.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No payload provided."}), 400

        image_id = data.get("image_id")
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}.jpg") if image_id else None
        heatmap_path = os.path.join(app.config["UPLOAD_FOLDER"], f"heatmap_{image_id}.jpg") if image_id else None
        if heatmap_path and not os.path.exists(heatmap_path):
            heatmap_path = None

        inspection_id = data.get("inspection_id", f"INSP-{uuid.uuid4().hex[:6].upper()}")
        date_time_str = data.get("date_time") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Digital E-Signature decoding if provided
        signature_path = None
        signature_data = data.get("signature_data")
        if signature_data:
            try:
                sig_pil = decode_base64_image(signature_data)
                sig_filename = f"sig_{inspection_id}.png"
                signature_path = os.path.join(app.config["UPLOAD_FOLDER"], sig_filename)
                sig_pil.save(signature_path, "PNG")
            except Exception as e:
                print(f"[WARNING] Failed to decode signature: {e}")

        report_payload = {
            "inspector_name": data.get("inspector_name", "N/A"),
            "vehicle_no": data.get("vehicle_no", "N/A"),
            "policy_no": data.get("policy_no", "N/A"),
            "inspection_id": inspection_id,
            "date_time": date_time_str,
            "notes": data.get("notes", "No remarks entered."),
            "prediction": data.get("prediction", "Unknown"),
            "summary": data.get("summary", ""),
            "framework": data.get("framework", "PyTorch 2.13.0"),
            "inference_time_ms": data.get("inference_time_ms", 0),
            "image_path": image_path,
            "heatmap_path": heatmap_path,
            "signature_path": signature_path
        }

        report_filename = f"report_{inspection_id}.pdf"
        output_pdf_path = os.path.join(app.config["REPORT_FOLDER"], report_filename)

        # Generate PDF using ReportLab
        generate_pdf_report(report_payload, output_pdf_path)

        return jsonify({
            "status": "success",
            "filename": report_filename,
            "report_url": f"/download_report/{report_filename}"
        }), 200

    except Exception as e:
        print(f"[ERROR] PDF Generation Exception: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to generate PDF report: {str(e)}"
        }), 500

@app.route("/download_report/<filename>")
def download_report(filename):
    """Serves the generated PDF Inspection Report (inline for printing, attachment for download)."""
    is_download = request.args.get("download", "1") == "1"
    return send_from_directory(
        app.config["REPORT_FOLDER"],
        filename,
        as_attachment=is_download,
        mimetype="application/pdf"
    )

@app.route("/uploads/<filename>")
def serve_upload(filename):
    """Serves uploaded vehicle images."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[SERVER START] Starting AI Vehicle Damage Assessment System on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
