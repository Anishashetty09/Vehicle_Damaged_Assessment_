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

    def predict(self, input_tensor):
        """
        Performs PyTorch binary classification inference.
        Returns ONLY genuine binary model prediction (Damaged vs No Damage Detected).
        No fabricated damage types, severity meters, or fake cost estimates.
        """
        input_tensor = input_tensor.to(self.device)
        
        start_time = time.perf_counter()
        
        with torch.no_grad():
            logits = self.model(input_tensor)
            probabilities = F.softmax(logits, dim=1)[0]
            
        end_time = time.perf_counter()
        inference_time_ms = round((end_time - start_time) * 1000, 2)
        
        predicted_class_idx = int(torch.argmax(probabilities).item())
        raw_label = CLASS_NAMES[predicted_class_idx]

        if raw_label == "Damaged":
            prediction = "Damaged"
            status_text = "Damaged"
            is_damaged = True
            summary = "The AI model detected visible signs that indicate the vehicle is damaged. This prediction is based on image analysis."
        else:
            prediction = "No Damage Detected"
            status_text = "No Damage Detected"
            is_damaged = False
            summary = "The AI model did not detect visible damage in the uploaded image."

        return {
            "prediction": prediction,
            "status_text": status_text,
            "is_damaged": is_damaged,
            "summary": summary,
            "inference_time_ms": inference_time_ms,
            "framework": f"PyTorch {torch.__version__}",
            "device": str(self.device).upper()
        }

# Singleton accessor function
def get_model_handler():
    return PyTorchModelHandler()
