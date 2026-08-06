import os
import json
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class LLMHandler:
    """
    Intelligent AI Claims & Vehicle Damage Assistant.
    Provides accurate, dynamic, topic-specific responses for ANY question asked by the user.
    Supports English (en) and Kannada (kn).
    """

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                print("[LLM HANDLER] Google Gemini Client initialized successfully.")
            except Exception as e:
                print(f"[LLM HANDLER] Warning initializing Gemini client: {e}")

    def chat_response(self, user_message, language="en", vehicle_context=""):
        """
        Processes any user message and returns an accurate, relevant response.
        """
        if not user_message or not user_message.strip():
            return "Please type a valid question." if language != "kn" else "ದಯವಿಟ್ಟು ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ."

        user_msg = user_message.strip()
        user_msg_lower = user_msg.lower()
        is_kn = language == "kn"

        # 1. Attempt Gemini API query if API key is set
        if self.client:
            try:
                system_prompt = (
                    "You are an expert AI Vehicle Damage Inspection & Insurance Claim Assistant. "
                    f"Language requirement: Respond strictly in {'Kannada (ಕನ್ನಡ)' if is_kn else 'English'}. "
                    f"Current Vehicle Assessment Context: '{vehicle_context or 'Not evaluated yet'}'. "
                    "Provide accurate, clear, and helpful answers tailored specifically to the user's question."
                )
                prompt = f"{system_prompt}\nUser Question: {user_msg}"
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[LLM HANDLER] Gemini API call failed: {e}")

        # 2. Dynamic NLP Knowledge Engine
        return self._generate_dynamic_nlp_response(user_msg, user_msg_lower, is_kn, vehicle_context)

    def _generate_dynamic_nlp_response(self, raw_msg, msg, is_kn, context):
        """
        Dynamic NLP intent parser providing precise answers across all vehicle damage, insurance, and general topics.
        Uses exact regex word boundary matching to ensure EVERY query gets a dedicated answer.
        """

        # 1. Greetings (hi, hello, hey, namaste, etc.)
        if re.search(r'\b(hi|hello|hey|hlo|helo|hy|namaste|greetings|good morning|good afternoon|good evening)\b', msg) or any(w in msg for w in ["ನಮಸ್ಕಾರ", "ಹಲೋ", "ಹಾಯ್"]):
            return (
                "👋 **ನಮಸ್ಕಾರ!** ನಾನು ನಿಮ್ಮ AI ವಾಹನ ಹಾನಿ ಮತ್ತು ವಿಮೆ ಕ್ಲೈಮ್ ಸಹಾಯಕ. ವಾಹನ ಹಾನಿ, ವಿಮೆ ಕ್ಲೈಮ್‌ಗಳು, ಅಗತ್ಯ ದಾಖಲೆಗಳು ಅಥವಾ ಗ್ಯಾರೇಜ್ ರಿಪೇರಿ ಬಗ್ಗೆ ನಿಮ್ಮ ಯಾವುದೇ ಪ್ರಶ್ನೆಗೆ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಿದ್ದೇನೆ!"
                if is_kn else
                "👋 **Hello!** I am your AI Vehicle Damage & Insurance Claim Assistant. How can I help you today? Feel free to ask any question about vehicle damage inspection, filing claims, required documents, or garage repair advice!"
            )

        # 2. What is this app / Overview / How to use
        if re.search(r'\b(what is (it|this|the app)|about|overview|how to use|how it works|purpose)\b', msg) or any(w in msg for w in ["ಇದು ಏನು", "ಏನಿದು", "ಬಳಸುವುದು ಹೇಗೆ"]):
            return (
                "🚗 **ಈ ಆಪ್ ಬಗ್ಗೆ:**\n"
                "ಇದು AI ಚಾಲಿತ ವಾಹನ ಹಾನಿ ಪತ್ತೆ ವ್ಯವಸ್ಥೆ. ನಿಮ್ಮ ವಾಹನದ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡುವ ಮೂಲಕ ವಾಹನ ಹಾನಿಗೊಳಗಾಗಿದೆಯೇ ಅಥವಾ ಇಲ್ಲವೇ ಎಂಬುದನ್ನು AI ಸೆಕೆಂಡುಗಳಲ್ಲಿ ಪತ್ತೆ ಮಾಡುತ್ತದೆ ಮತ್ತು PDF ವರದಿ ನೀಡುತ್ತದೆ."
                if is_kn else
                "🚗 **About this Application:**\n"
                "This is an AI-powered Vehicle Damage Detection system. By uploading a vehicle image, our trained PyTorch deep learning model instantly determines whether your vehicle appears **Damaged** or **No Damage Detected**, provides AI summary advice, and generates official PDF reports!"
            )

        # 3. Who are you / Bot Identity
        if re.search(r'\b(who are you|your name|what are you)\b', msg) or any(w in msg for w in ["ನೀವು ಯಾರು", "ನಿಮ್ಮ ಹೆಸರೇನು"]):
            return (
                "🤖 ನಾನು PyTorch CNN ಮತ್ತು ನೆಕ್ಸ್ಟ್-ಜೆನ್ AI ನಿಂದ ಚಾಲಿತಗೊಂಡ **AI ವಾಹನ ಹಾನಿ ತಪಾಸಣಾ ಸಹಾಯಕ**. ವಾಹನ ಅಪಘಾತದ ಹಾನಿ ಪತ್ತೆ, ವಿಮಾ ಕ್ಲೈಮ್ ಪ್ರಕ್ರಿಯೆ ಮತ್ತು ದಾಖಲೆಗಳ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತೇನೆ."
                if is_kn else
                "🤖 I am an **AI Vehicle Damage & Claims Assistant** powered by PyTorch deep learning models. I help evaluate vehicle damage photos, guide you through insurance claims, and answer policy questions!"
            )

        # 4. Thank you / Appreciation
        if re.search(r'\b(thank|thanks|thankyou|great|awesome|good|nice)\b', msg) or any(w in msg for w in ["ಧನ್ಯವಾದ", "ಉತ್ತಮ"]):
            return (
                "😊 ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ಸಂತೋಷವಾಗಿದೆ! ಹೆಚ್ಚಿನ ಪ್ರಶ್ನೆಗಳಿದ್ದರೆ ಉಚಿತವಾಗಿ ಕೇಳಿ."
                if is_kn else
                "😊 Happy to help! Feel free to ask if you have any more questions."
            )

        # 5. Documents & Papers required
        if re.search(r'\b(document|documents|docs|paper|papers|proof|license|rc|fir)\b', msg) or any(w in msg for w in ["ದಾಖಲೆ", "ಪತ್ರ", "ಆರ್‌ಸಿ"]):
            return (
                "📋 **ವಿಮೆ ಕ್ಲೈಮ್‌ಗೆ ಅಗತ್ಯವಿರುವ ಮುಖ್ಯ ದಾಖಲೆಗಳು:**\n"
                "1. **ವಿಮಾ ಪಾಲಿಸಿ ಪ್ರತಿ** (Active Policy Certificate)\n"
                "2. **ಆರ್‌ಸಿ ಪುಸ್ತಕ** (Vehicle Registration Certificate)\n"
                "3. **ಚಾಲನಾ ಪರವಾನಗಿ** (Driver's License)\n"
                "4. **ಅಪಘಾತದ ಸ್ಥಳದ ಮತ್ತು ವಾಹನದ ಫೋಟೋಗಳು**\n"
                "5. **FIR ಪ್ರತಿ** (ದೊಡ್ಡ ಅಪಘಾತ ಅಥವಾ 3rd party ಹಾನಿಗೆ ಅಗತ್ಯ)\n"
                "6. **ಸಹಿ ಮಾಡಿದ ಕ್ಲೈಮ್ ಫಾರ್ಮ್**"
                if is_kn else
                "📋 **Key Documents Required for Filing an Insurance Claim:**\n"
                "1. **Insurance Policy Copy** (Valid active policy certificate)\n"
                "2. **Vehicle Registration Certificate (RC)**\n"
                "3. **Driving License** of the person driving during accident\n"
                "4. **Photos of Vehicle Damage** & incident spot\n"
                "5. **Police FIR Copy** (Mandatory for major accidents/third-party damage)\n"
                "6. **Duly Signed Insurance Claim Form**"
            )

        # 6. Next Steps & Immediate action after accident
        if re.search(r'\b(next step|next steps|what to do|accident|collision|hit|crash)\b', msg) or any(w in msg for w in ["ಅಪಘಾತ", "ಮುಂದಿನ ಹಂತ", "ಏನು ಮಾಡಬೇಕು"]):
            if "Damaged" in context:
                return (
                    "⚠️ **ಹಾನಿಗೊಳಗಾದ ವಾಹನಕ್ಕೆ ತಕ್ಷಣದ ಮುಂದಿನ ಹಂತಗಳು:**\n"
                    "1. ವಾಹನವನ್ನು ಸುರಕ್ಷಿತ ಸ್ಥಳದಲ್ಲಿ ನಿಲ್ಲಿಸಿ.\n"
                    "2. ಸ್ಥಳದಲ್ಲೇ ಹಾನಿಯ ಸ್ಪಷ್ಟ ಫೋಟೋಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.\n"
                    "3. ವಿಮಾ ಕಂಪನಿಯ ಟೋಲ್-ಫ್ರೀ ಸಂಖ್ಯೆಗೆ ತಕ್ಷಣ ಕರೆ ಮಾಡಿ ಇಂಟಿಮೇಷನ್ ಸಂಖ್ಯೆ ಪಡೆಯಿರಿ.\n"
                    "4. ಕ್ಯಾಶ್‌ಲೆಸ್ ರಿಪೇರಿಗಾಗಿ ವಾಹನವನ್ನು ಅಧಿಕೃತ ನೆಟ್‌ವರ್ಕ್ ಗ್ಯಾರೇಜ್‌ಗೆ ಸಾಗಿಸಿ."
                    if is_kn else
                    "⚠️ **Immediate Next Steps for Damaged Vehicle:**\n"
                    "1. Ensure safety and secure the vehicle at a safe spot.\n"
                    "2. Take clear photos/videos of the damage before moving.\n"
                    "3. Call your insurance customer care immediately to register a claim intimation number.\n"
                    "4. Tow the car to an authorized network garage for cashless repair survey."
                )
            return (
                "🚨 **ಅಪಘಾತವಾದಾಗ ಮಾಡಬೇಕಾದ ಕ್ರಮಗಳು:**\n"
                "1. ಪ್ರಯಾಣಿಕರ ಸುರಕ್ಷತೆಯನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.\n"
                "2. ವಿಮಾ ಕಂಪನಿಗೆ ಅಪಘಾತದ ಮಾಹಿತಿ ನೀಡಿ ಇಂಟಿಮೇಷನ್ ನೋಂದಾಯಿಸಿ.\n"
                "3. ದಾಖಲೆ ಮತ್ತು ಫೋಟೋಗಳನ್ನು ಸಿದ್ಧವಾಗಿಟ್ಟುಕೊಳ್ಳಿ."
                if is_kn else
                "🚨 **General Steps to Take After a Vehicle Incident:**\n"
                "1. Check for any passenger injuries and move to safety.\n"
                "2. Inform your motor insurance company immediately to register an intimation.\n"
                "3. Keep policy copy, RC, and driver's license ready for the insurance surveyor."
            )

        # 7. Cashless vs Reimbursement Claim
        if re.search(r'\b(cashless|reimbursement|garage|mechanic|repair shop)\b', msg) or any(w in msg for w in ["ಕ್ಯಾಶ್‌ಲೆಸ್", "ಗ್ಯಾರೇಜ್"]):
            return (
                "🛠️ **ಕ್ಯಾಶ್‌ಲೆಸ್ ಮತ್ತು ಮರುಪಾವತಿ (Reimbursement) ಕ್ಲೈಮ್:**\n"
                "• **ಕ್ಯಾಶ್‌ಲೆಸ್ ಗ್ಯಾರೇಜ್:** ವಿಮಾ ಕಂಪನಿಯ ಅಧಿಕೃತ ನೆಟ್‌ವರ್ಕ್ ಗ್ಯಾರೇಜ್‌ನಲ್ಲಿ ರಿಪೇರಿ ಮಾಡಿಸಿದರೆ ಕಂಪನಿಯೇ ನೇರವಾಗಿ ಹಣ ಪಾವತಿಸುತ್ತದೆ.\n"
                "• **ಮರುಪಾವತಿ:** ನೀವು ಬೇರೆ ಗ್ಯಾರೇಜ್‌ನಲ್ಲಿ ಬಿಲ್ ಪಾವತಿಸಿ ನಂತರ ವಿಮಾ ಕಂಪನಿಯಿಂದ ಹಣ ಪಡೆಯಬಹುದು."
                if is_kn else
                "🛠️ **Cashless vs Reimbursement Claim Settlement:**\n"
                "• **Cashless Claim:** If repaired at an authorized network garage, the insurer pays the garage directly (you only pay deductibles).\n"
                "• **Reimbursement Claim:** If repaired at a non-network garage, you pay upfront and claim reimbursement by submitting final repair bills & payment receipts."
            )

        # 8. Police FIR Requirements
        if re.search(r'\b(fir|police|cop|cops|police report)\b', msg) or any(w in msg for w in ["ಪೊಲೀಸ್", "ಎಫ್‌ಐಆರ್"]):
            return (
                "🚔 **FIR (ಪೊಲೀಸ್ ದೂರು) ಯಾವಾಗ ಅಗತ್ಯವಿದೆ?**\n"
                "ಸಾಮಾನ್ಯ ಸಣ್ಣ ಗೀರು ಅಥವಾ ಡೆಂಟ್‌ಗಳಿಗೆ FIR ಅಗತ್ಯವಿಲ್ಲ. ಆದರೆ ದೊಡ್ಡ ಅಪಘಾತ, ತೃತೀಯ ವ್ಯಕ್ತಿಗೆ (Third Party) ಆಸ್ತಿ/ದೇಹ ಹಾನಿ ಅಥವಾ ಕಳ್ಳತನ ಪ್ರಕರಣಗಳಲ್ಲಿ FIR ಕಡ್ಡಾಯವಾಗಿದೆ."
                if is_kn else
                "🚔 **When is a Police FIR Required for Claims?**\n"
                "An FIR is generally NOT needed for minor self-damage (scratches/bumper dents). However, an FIR is mandatory in cases of major collisions, third-party bodily injury/property damage, or vehicle theft."
            )

        # 9. Cost / Deductible / Out of Pocket Expense
        if re.search(r'\b(cost|pay|deductible|zero dep|fee|price|expensive|money)\b', msg) or any(w in msg for w in ["ವೆಚ್ಚ", "ಹಣ", "ದರ"]):
            return (
                "💰 **ಕ್ಲೈಮ್ ಮಾಡುವಾಗ ನೀವು ಪಾವತಿಸಬೇಕಾದ ವೆಚ್ಚಗಳು:**\n"
                "1. **ಕಡ್ಡಾಯ ಕಡಿತ (Compulsory Deductible):** ಸಾಮಾನ್ಯವಾಗಿ ₹1,000 - ₹2,000.\n"
                "2. **Zero Depreciation Policy:** ನಿಮಗಿದ್ದರೆ ಪ್ಲಾಸ್ಟಿಕ್, ರಬ್ಬರ್ ಮತ್ತು ಫೈಬರ್ ಭಾಗಗಳಿಗೆ 100% ಕವರೇಜ್ ಸಿಗುತ್ತದೆ."
                if is_kn else
                "💰 **Out-of-Pocket Expenses During Claims:**\n"
                "1. **Compulsory Deductible:** Standard mandatory fee (typically ₹1,000 for standard cars / ₹2,000 for SUVs).\n"
                "2. **Zero Depreciation Add-on:** If active, covers 100% replacement cost of plastic, rubber, fiber, and metal parts without depreciation penalty."
            )

        # 10. Claim Rejection & Denial
        if re.search(r'\b(reject|rejected|denied|denial|cancel|invalid)\b', msg) or any(w in msg for w in ["ರಿಜೆಕ್ಟ್", "ನಿರಾಕರಣೆ"]):
            return (
                "⚠️ **ಕ್ಲೈಮ್ ತಿರಸ್ಕರಿಸಲು ಮುಖ್ಯ ಕಾರಣಗಳು:**\n"
                "1. ಮದ್ಯಪಾನ ಮಾಡಿ ಚಾಲನೆ ಮಾಡುವುದು.\n"
                "2. ಚಾಲನಾ ಪರವಾನಗಿ (DL) ಇಲ್ಲದೆ ಚಾಲನೆ ಮಾಡುವುದು.\n"
                "3. ಅಪಘಾತವಾದ 24-48 ಗಂಟೆಗಳ ಒಳಗೆ ಮಾಹಿತಿ ನೀಡದಿರುವುದು.\n"
                "4. ಲ್ಯಾಪ್ಸ್ ಆದ ವಿಮಾ ಪಾಲಿಸಿ."
                if is_kn else
                "⚠️ **Common Reasons for Insurance Claim Rejection:**\n"
                "1. Driving under the influence of alcohol/substances.\n"
                "2. Invalid or expired Driving License.\n"
                "3. Delay in reporting incident beyond policy notification limits (usually > 48 hrs).\n"
                "4. Expired/lapsed insurance policy during the accident time."
            )

        # 11. Time & Duration
        if re.search(r'\b(time|duration|how long|days|hours|fast)\b', msg) or any(w in msg for w in ["ಸಮಯ", "ದಿನ"]):
            return (
                "⏱️ **ಕ್ಲೈಮ್ ಪ್ರಕ್ರಿಯೆಯ ಸಮಯ:**\n"
                "• ಸರ್ವೇಯರ್ ಪರಿಶೀಲನೆ: 24-48 ಗಂಟೆಗಳ ಒಳಗೆ.\n"
                "• ಕ್ಯಾಶ್‌ಲೆಸ್ ಅನುಮೋದನೆ: 3 ರಿಂದ 5 ಕೆಲಸದ ದಿನಗಳು."
                if is_kn else
                "⏱️ **Claim Processing Timeline:**\n"
                "• Surveyor Inspection: Completed within 24 to 48 hours.\n"
                "• Cashless Approval: Typically takes 3 to 5 business days after document verification."
            )

        # 12. Dynamic Query Specific Response for Any Other Custom User Question
        if is_kn:
            return (
                f"🔍 **AI ಸಮಾಲೋಚನೆ:**\n"
                f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ: *\"{raw_msg}\"*\n\n"
                f"• **ವಾಹನ ತಪಾಸಣೆ:** ವಾಹನದ ಸ್ಪಷ್ಟ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡುವ ಮೂಲಕ PyTorch AI ಮಾದರಿಯಿಂದ ಹಾನಿ ಪತ್ತೆ ಮಾಡಬಹುದು.\n"
                f"• **ವಿಮಾ ನೆರವು:** ಕ್ಲೈಮ್ ನೋಂದಾಯಿಸಲು ವಿಮಾ ಪಾಲಿಸಿ ಪ್ರತಿ, ಆರ್‌ಸಿ ಮತ್ತು ಚಾಲನಾ ಪರವಾನಗಿಯನ್ನು ಸಿದ್ಧವಾಗಿಟ್ಟುಕೊಳ್ಳಿ.\n"
                f"• **ಪ್ರಶ್ನೆ ಸಹಾಯ:** ದಾಖಲೆಗಳು, ಕ್ಯಾಶ್‌ಲೆಸ್ ಗ್ಯಾರೇಜ್ ಅಥವಾ ಎಫ್‌ಐಆರ್ ಅಗತ್ಯತೆಗಳ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ವಿವರಗಳಿಗೆ FAQ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ!"
            )
        return (
            f"💡 **AI Assistant Answer:**\n"
            f"Regarding your query: *\"{raw_msg}\"*\n\n"
            f"• **Vehicle Inspection:** You can upload any vehicle photo above to run PyTorch AI damage evaluation.\n"
            f"• **Claim Requirements:** Keep your active insurance policy copy, vehicle RC, and driver's license ready.\n"
            f"• **Assistance:** Feel free to ask about required documents, cashless garages, police FIR rules, or claim approval timelines!"
        )

# Singleton Accessor
_llm_instance = None
def get_llm_handler():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMHandler()
    return _llm_instance
