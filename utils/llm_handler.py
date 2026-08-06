import os
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class LLMHandler:
    """
    LLM Claims & Damage Assistant Handler.
    Uses Google Gemini API if GEMINI_API_KEY is available;
    otherwise uses a smart contextual fallback engine.
    Supports English (en) and Kannada (kn) languages.
    """

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                print("[LLM HANDLER] Google Gemini Client initialized successfully.")
            except Exception as e:
                print(f"[LLM HANDLER] Warning initializing Gemini client: {e}")
                self.client = None
        else:
            self.client = None
            print("[LLM HANDLER] Running in Fallback Mode (No GEMINI_API_KEY provided).")

    def chat_response(self, user_message, language="en", vehicle_context=""):
        """
        Generates an accurate, professional response to user queries.
        Supports Kannada (kn) and English (en).
        """
        user_msg_lower = user_message.lower()
        is_kn = language == "kn"

        # Check for specific FAQ topics first for guaranteed accuracy
        if any(w in user_msg_lower for w in ["document", "docs", "paper", "ದಾಖಲೆ"]):
            return self._get_documents_required_response(is_kn)
        elif any(w in user_msg_lower for w in ["next step", "process", "what to do", "ಮುಂದಿನ ಹಂತ"]):
            return self._get_next_steps_response(is_kn, vehicle_context)
        elif any(w in user_msg_lower for w in ["how it works", "ai work", "detection", "ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ"]):
            return self._get_how_it_works_response(is_kn)
        elif any(w in user_msg_lower for w in ["time", "duration", "how long", "ಸಮಯ"]):
            return self._get_claim_duration_response(is_kn)

        # Attempt Gemini API query if client is available
        if self.client:
            try:
                system_prompt = (
                    "You are an expert AI Vehicle Damage Inspection & Insurance Claim Assistant. "
                    f"Language requirement: Respond strictly in {'Kannada (ಕನ್ನಡ)' if is_kn else 'English'}. "
                    f"Context: The vehicle evaluation status is '{vehicle_context or 'Unknown'}'. "
                    "Keep responses concise, professional, clear, and helpful."
                )
                prompt = f"{system_prompt}\nUser Question: {user_message}"
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[LLM HANDLER] Gemini API call failed: {e}")

        # Smart fallback response
        return self._get_general_fallback_response(user_message, is_kn, vehicle_context)

    def _get_documents_required_response(self, is_kn):
        if is_kn:
            return (
                "📋 **ವಿಮೆ ಕ್ಲೈಮ್‌ಗೆ ಅಗತ್ಯವಿರುವ ಮುಖ್ಯ ದಾಖಲೆಗಳು:**\n"
                "1. **ವಿಮಾ ಪಾಲಿಸಿ ಪ್ರತಿ** (Insurance Policy Document)\n"
                "2. **ವಾಹನ ಆರ್‌ಸಿ ಪುಸ್ತಕ** (Vehicle Registration Certificate - RC)\n"
                "3. **ಚಾಲನಾ ಪರವಾನಗಿ** (Driver's License)\n"
                "4. **ಅಪಘಾತ ಸ್ಥಳದ ಮತ್ತು ವಾಹನದ ಫೋಟೋಗಳು** (Photos of Vehicle Damage)\n"
                "5. **FIR ಪ್ರತಿ** (ದೊಡ್ಡ ಅಪಘಾತ ಅಥವಾ ಕಳ್ಳತನ ಪ್ರಕರಣಗಳಿಗೆ)\n"
                "6. **ಭರ್ತಿ ಮಾಡಿದ ಕ್ಲೈಮ್ ಫಾರ್ಮ್** (Filled Claim Form)"
            )
        return (
            "📋 **Key Documents Required for Filing an Insurance Claim:**\n"
            "1. **Insurance Policy Copy** (Active policy details)\n"
            "2. **Vehicle Registration Certificate (RC)**\n"
            "3. **Driver's License** of the person driving\n"
            "4. **Vehicle Damage Photographs** (Captured on-site)\n"
            "5. **FIR Copy** (Required in case of major collisions or third-party injury)\n"
            "6. **Completed & Signed Claim Form**"
        )

    def _get_next_steps_response(self, is_kn, context):
        if is_kn:
            if "Damaged" in context:
                return (
                    "⚠️ **ವಾಹನ ಹಾನಿಗೊಳಗಾದಾಗ ಮಾಡಬೇಕಾದ ಮುಂದಿನ ಹಂತಗಳು:**\n"
                    "1. ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ವಾಹನವನ್ನು ನಿಲ್ಲಿಸಿ.\n"
                    "2. ಹಾನಿಗೊಳಗಾದ ಭಾಗಗಳ ಸ್ಪಷ್ಟ ಫೋಟೋಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.\n"
                    "3. ನಿಮ್ಮ ವಿಮಾ ಕಂಪನಿಯ ಟೋಲ್-ಫ್ರೀ ಸಂಖ್ಯೆಗೆ ತಕ್ಷಣವೇ ಕರೆ ಮಾಡಿ ಅಪಘಾತ ವರದಿ ಮಾಡಿ.\n"
                    "4. ನೆಟ್‌ವರ್ಕ್ ಗ್ಯಾರೇಜ್‌ಗೆ ವಾಹನವನ್ನು ಶಿಫ್ಟ್ ಮಾಡಿ ಮತ್ತು ಸರ್ವೇಯರ್ ಪರಿಶೀಲನೆಗೆ ಸಹಕರಿಸಿ."
                )
            return (
                "✅ **ಮುಂದಿನ ಹಂತಗಳು:**\n"
                "ನಿಮ್ಮ ವಾಹನದಲ್ಲಿ ಯಾವುದೇ ಹಾನಿ ಕಂಡುಬಂದಿಲ್ಲ. ಸಾಮಾನ್ಯ ವಾಹನ ಚಾಲನೆ ಮುಂದುವರಿಸಬಹುದು."
            )
        
        if "Damaged" in context:
            return (
                "⚠️ **Recommended Next Steps for Damaged Vehicle:**\n"
                "1. Ensure passenger safety and move to a secure location.\n"
                "2. Document the incident with photos of the vehicle.\n"
                "3. Notify your insurance provider immediately to open a claim file.\n"
                "4. Transport the vehicle to an authorized network garage for surveyor inspection."
            )
        return (
            "✅ **Next Steps:**\n"
            "No exterior damage was detected. Your vehicle passed evaluation."
        )

    def _get_how_it_works_response(self, is_kn):
        if is_kn:
            return (
                "🤖 **AI ವಾಹನ ಹಾನಿ ಪತ್ತೆ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ?**\n"
                "ನಮ್ಮ ಸಿಸ್ಟಮ್ PyTorchConvolutional Neural Network (CNN) ಮಾದರಿಯನ್ನು ಬಳಸುತ್ತದೆ. "
                "ಇದು ಚಿತ್ರದಲ್ಲಿನ ಪ್ರತಿಯೊಂದು ವಿವರವನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ ವಾಹನ ಹಾನಿಗೊಳಗಾಗಿದೆಯೇ ಅಥವಾ ಇಲ್ಲವೇ ಎಂಬುದನ್ನು ಸೆಕೆಂಡುಗಳಲ್ಲಿ ನಿಖರವಾಗಿ ಪತ್ತೆ ಮಾಡುತ್ತದೆ."
            )
        return (
            "🤖 **How AI Vehicle Damage Detection Works:**\n"
            "Our system runs a trained PyTorch Convolutional Neural Network (CNN) model. "
            "It scans visual pixel features from your uploaded photo to accurately classify the vehicle as **Damaged** or **No Damage Detected** within milliseconds."
        )

    def _get_claim_duration_response(self, is_kn):
        if is_kn:
            return (
                "⏱️ **ಕ್ಲೈಮ್ ಅನುಮೋದನೆಗೆ ಎಷ್ಟು ಸಮಯ ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ?**\n"
                "ಸಾಮಾನ್ಯವಾಗಿ ವಿಮಾ ಕಂಪನಿಗಳು 24 ರಿಂದ 48 ಗಂಟೆಗಳ ಒಳಗೆ ಸರ್ವೇಯರ್ ತಪಾಸಣೆ ಪೂರ್ಣಗೊಳಿಸುತ್ತವೆ. "
                "ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಸಲ್ಲಿಸಿದ ನಂತರ 3-5 ಕೆಲಸದ ದಿನಗಳಲ್ಲಿ ಕ್ಲೈಮ್ ಅನುಮೋದನೆಯಾಗುತ್ತದೆ."
            )
        return (
            "⏱️ **Insurance Claim Approval Duration:**\n"
            "Typically, surveyors complete physical inspection within 24 to 48 hours. "
            "Once required documents are submitted, cashless approvals are usually processed in 3 to 5 business days."
        )

    def _get_general_fallback_response(self, query, is_kn, context):
        if is_kn:
            return (
                "🤖 **AI ಸಹಾಯಕ:**\n"
                f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ: '{query}'\n\n"
                "ವಾಹನ ಹಾನಿ ತಪಾಸಣೆ ಮತ್ತು ವಿಮೆ ಕ್ಲೈಮ್‌ಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಸಿದ್ಧನಿದ್ದೇನೆ. "
                "ನಿಮಗೆ ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು, ಪ್ರಕ್ರಿಯೆ ಅಥವಾ ಮುಂದಿನ ಹಂತಗಳ ಬಗ್ಗೆ ಉಚಿತವಾಗಿ ಕೇಳಬಹುದು."
            )
        return (
            "🤖 **AI Claims Assistant:**\n"
            f"Regarding your query: '{query}'\n\n"
            "I can assist you with vehicle damage inspection guidelines, claim documentation, garage repair steps, and policy questions. Feel free to select any of the suggested questions above!"
        )

# SingletonAccessor
_llm_instance = None
def get_llm_handler():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMHandler()
    return _llm_instance
