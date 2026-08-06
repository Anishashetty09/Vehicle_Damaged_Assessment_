import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import uuid
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from utils.image_processor import decode_base64_image, process_image
from utils.model_handler import get_model_handler
from utils.pdf_generator import generate_pdf_report
from utils.llm_handler import get_llm_handler

# Initialize Flask application
app = Flask(__name__, static_folder="static", template_folder="templates")

# Configure directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload limit

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
    Executes PyTorch model inference in evaluation mode with torch.no_grad().
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

        # Save snapshot into uploads/ directory
        image_id = f"img_{uuid.uuid4().hex[:10]}"
        image_filename = f"{image_id}.jpg"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        
        # Ensure RGB format and save JPEG
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        pil_image.save(image_path, "JPEG", quality=92)

        # Apply TorchVision Preprocessing
        input_tensor, _ = process_image(pil_image)

        # Run PyTorch Model Inference
        result = model_handler.predict(input_tensor)
        
        # Append metadata
        result["status"] = "success"
        result["image_id"] = image_id
        result["image_url"] = f"/uploads/{image_filename}"

        return jsonify(result), 200

    except Exception as e:
        print(f"[ERROR] Inference Exception: {e}")
        return jsonify({
            "status": "error",
            "message": f"Inference processing failed: {str(e)}"
        }), 500

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
    Accepts inspector details, prediction results, and generates ReportLab PDF.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No payload provided."}), 400

        image_id = data.get("image_id")
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{image_id}.jpg") if image_id else None

        inspection_id = data.get("inspection_id", f"INSP-{uuid.uuid4().hex[:6].upper()}")
        date_time_str = data.get("date_time") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            "image_path": image_path
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
    """Serves the generated PDF Inspection Report."""
    return send_from_directory(app.config["REPORT_FOLDER"], filename, as_attachment=True)

@app.route("/uploads/<filename>")
def serve_upload(filename):
    """Serves uploaded vehicle images."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[SERVER START] Starting AI Vehicle Damage Assessment System on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
