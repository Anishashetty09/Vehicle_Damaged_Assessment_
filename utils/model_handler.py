import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import time
import torch
import torch.nn.functional as F
from models.vehicle_damage_model import get_model

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "vehicle_damage_model.pth")
CLASS_NAMES = {0: "Damaged", 1: "Whole"}

class PyTorchModelHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PyTorchModelHandler, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """
        Loads the PyTorch model architecture and weights in evaluation mode.
        """
        print(f"[MODEL HANDLER] Loading PyTorch model from: {MODEL_PATH}")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = get_model(num_classes=2, pretrained=False)
        
        if os.path.exists(MODEL_PATH):
            state_dict = torch.load(MODEL_PATH, map_location=self.device)
            self.model.load_state_dict(state_dict)
            print("[MODEL HANDLER] PyTorch state_dict loaded successfully.")
        else:
            print("[WARNING] PyTorch model checkpoint file not found! Initializing default weights.")

        self.model.to(self.device)
        self.model.eval()  # Set model to evaluation mode
        print(f"[MODEL HANDLER] Model running on device: {self.device} in eval mode (torch.no_grad active)")

    def predict(self, pil_image):
        """
        Performs PyTorch binary classification inference with Test-Time Augmentation (TTA)
        and Grad-CAM visual heatmap generation for maximum accuracy and reliability.
        """
        from utils.image_processor import get_tta_tensors, generate_gradcam_heatmap, overlay_heatmap_on_image
        
        start_time = time.perf_counter()

        # 1. Test-Time Augmentation (TTA)
        tta_tensors = get_tta_tensors(pil_image).to(self.device)
        
        with torch.no_grad():
            logits = self.model(tta_tensors)
            probs_batch = F.softmax(logits, dim=1)
            # Average probabilities across the 3 TTA variations
            avg_probs = torch.mean(probs_batch, dim=0)

        end_time = time.perf_counter()
        inference_time_ms = round((end_time - start_time) * 1000, 2)
        
        predicted_class_idx = int(torch.argmax(avg_probs).item())
        raw_label = CLASS_NAMES[predicted_class_idx]
        
        prob_damaged = round(float(avg_probs[0].item()) * 100, 2)
        prob_whole = round(float(avg_probs[1].item()) * 100, 2)
        confidence_pct = prob_damaged if predicted_class_idx == 0 else prob_whole

        # 2. Grad-CAM Visual Heatmap Generation
        single_tensor = tta_tensors[:1]
        heatmap_2d = generate_gradcam_heatmap(self.model, single_tensor, self.device, target_class=0)
        heatmap_pil = overlay_heatmap_on_image(pil_image, heatmap_2d)

        # 3. Calibration check
        is_uncertain = 45.0 <= prob_damaged <= 55.0

        if raw_label == "Damaged":
            prediction = "Damaged"
            status_text = "Damaged"
            is_damaged = True
            summary = "The AI model detected visible signs that indicate the vehicle is damaged. Grad-CAM visual heatmaps highlight affected regions."
        else:
            prediction = "No Damage Detected"
            status_text = "No Damage Detected"
            is_damaged = False
            summary = "The AI model did not detect visible damage in the uploaded vehicle image."

        return {
            "prediction": prediction,
            "status_text": status_text,
            "is_damaged": is_damaged,
            "confidence_percentage": confidence_pct,
            "damaged_probability": prob_damaged,
            "whole_probability": prob_whole,
            "is_uncertain": is_uncertain,
            "summary": summary,
            "inference_time_ms": inference_time_ms,
            "framework": f"PyTorch {torch.__version__}",
            "device": str(self.device).upper(),
            "heatmap_pil": heatmap_pil
        }

# Singleton accessor function
def get_model_handler():
    return PyTorchModelHandler()

