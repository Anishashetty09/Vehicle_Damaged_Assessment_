/**
 * Bilingual UI Dictionary (English & Kannada / ಕನ್ನಡ)
 */
const TRANSLATIONS = {
    en: {
        brand_title: "AI Vehicle Damage Detection",
        brand_subtitle: "Binary AI Image Classification",
        nav_home: "Home",
        nav_assessment: "Start Assessment",
        nav_assistant: "AI Assistant",
        nav_history: "History",
        model_ready: "Model Ready",
        
        hero_pill: "Binary AI Classification",
        hero_title: "AI Vehicle Damage Detection",
        hero_desc: "Upload or capture a vehicle image and let the AI determine whether the vehicle appears damaged or not damaged in just a few seconds.",
        btn_start_assessment: "Start Assessment",
        
        chip_damaged: "Damaged",
        chip_nodamage: "No Damage Detected",
        
        acquisition_tag: "Image Acquisition",
        acquisition_title: "Vehicle Damage Assessment",
        acquisition_desc: "Upload or capture a vehicle photo to evaluate exterior status.",
        
        tab_upload: "Upload Image",
        tab_camera: "Live Camera",
        
        dropzone_title: "Drag & Drop Vehicle Image Here",
        dropzone_sub: "or click to browse from your device",
        dropzone_formats: "Supports JPG, PNG, WEBP (Max 16MB)",
        
        cam_inactive: "Camera is inactive",
        cam_start: "Start Camera",
        cam_capture: "Capture Photo",
        cam_stop: "Stop",
        
        selected_img: "Selected Vehicle Image",
        btn_run_assessment: "Run Assessment",
        
        loading_title: "Analyzing Vehicle Image",
        loading_sub: "Evaluating model features...",
        step_uploading: "Uploading Image...",
        step_analyzing: "Analyzing Image...",
        step_running: "Running AI Model...",
        step_generating: "Generating Result...",
        
        res_header_tag: "Assessment Complete",
        res_header_title: "Prediction Result",
        res_header_sub: "Genuine classification output from the AI model.",
        
        res_uploaded_img: "Uploaded Image",
        res_vehicle_status: "Vehicle Status",
        res_model_pred: "MODEL PREDICTION",
        
        status_damaged: "Damaged",
        status_nodamage: "No Damage Detected",
        
        summary_title: "AI Summary",
        summary_damaged_text: "The AI model detected visible signs that indicate the vehicle is damaged. This prediction is based on image analysis.",
        summary_nodamage_text: "The AI model did not detect visible damage in the uploaded image.",
        
        btn_assess_another: "Assess Another Image",
        btn_upload_new: "Upload New Image",
        btn_return_home: "Return Home",
        btn_download_pdf: "Download Result as PDF",
        
        history_tag: "Local Logs",
        history_title: "Assessment History",
        history_sub: "Saved binary prediction records from your session.",
        btn_clear_history: "Clear History",
        history_empty: "No records saved yet. Complete an assessment to see history here.",
        
        th_time: "Timestamp",
        th_id: "Inspection ID",
        th_status: "Vehicle Status",
        th_actions: "Actions",
        
        footer_desc: "Genuine PyTorch Convolutional Neural Network binary classification system.",
        
        // Chatbot Widget Translations
        chat_header: "AI Claims Assistant",
        chat_sub: "Ask any question in English or ಕನ್ನಡ",
        chat_faq_title: "Frequently Asked Questions:",
        faq_1: "📋 What documents are required for a claim?",
        faq_2: "⚠️ What are the next steps if vehicle is damaged?",
        faq_3: "🤖 How does AI damage detection work?",
        faq_4: "⏱️ How long does claim approval take?",
        chat_placeholder: "Type a question or select an FAQ above...",
        chat_send: "Send"
    },
    kn: {
        brand_title: "AI ವಾಹನ ಹಾನಿ ಪತ್ತೆ ಸಿಸ್ಟಮ್",
        brand_subtitle: "ಬೈನರಿ AI ಇಮೇಜ್ ವರ್ಗೀಕರಣ",
        nav_home: "ಮುಖ್ಯ ಪುಟ",
        nav_assessment: "ತಪಾಸಣೆ ಪ್ರಾರಂಭಿಸಿ",
        nav_assistant: "AI ಸಹಾಯಕ",
        nav_history: "ಇತಿಹಾಸ",
        model_ready: "ಮಾದರಿ ಸಿದ್ಧವಾಗಿದೆ",
        
        hero_pill: "ಬೈನರಿ AI ವರ್ಗೀಕರಣ",
        hero_title: "AI ವಾಹನ ಹಾನಿ ಪತ್ತೆ",
        hero_desc: "ವಾಹನದ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ತೆಗೆಯಿರಿ ಮತ್ತು ವಾಹನ ಹಾನಿಗೊಳಗಾಗಿದೆಯೇ ಅಥವಾ ಇಲ್ಲವೇ ಎಂಬುದನ್ನು AI ಮೂಲಕ ಸೆಕೆಂಡುಗಳಲ್ಲಿ ತಿಳಿಯಿರಿ.",
        btn_start_assessment: "ತಪಾಸಣೆ ಪ್ರಾರಂಭಿಸಿ",
        
        chip_damaged: "ಹಾನಿಗೊಳಗಾಗಿದೆ (Damaged)",
        chip_nodamage: "ಯಾವುದೇ ಹಾನಿ ಇಲ್ಲ (No Damage)",
        
        acquisition_tag: "ಚಿತ್ರ ಸಂಗ್ರಹಣೆ",
        acquisition_title: "ವಾಹನ ಹಾನಿ ತಪಾಸಣೆ",
        acquisition_desc: "ವಾಹನದ ಬಾಹ್ಯ ಸ್ಥಿತಿಯನ್ನು ಮೌಲ್ಯಮಾಪನ ಮಾಡಲು ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಕ್ಯಾಪ್ಚರ್ ಮಾಡಿ.",
        
        tab_upload: "ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        tab_camera: "ಲೈವ್ ಕ್ಯಾಮೆರಾ",
        
        dropzone_title: "ವಾಹನದ ಚಿತ್ರವನ್ನು ಇಲ್ಲಿ ಡ್ರಾಗ್ ಮಾಡಿ",
        dropzone_sub: "ಅಥವಾ ನಿಮ್ಮ ಸಾಧನದಿಂದ ಆಯ್ಕೆ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ",
        dropzone_formats: "JPG, PNG, WEBP ಬೆಂಬಲಿತವಾಗಿದೆ (ಗರಿಷ್ಠ 16MB)",
        
        cam_inactive: "ಕ್ಯಾಮೆರಾ ನಿಷ್ಕ್ರಿಯವಾಗಿದೆ",
        cam_start: "ಕ್ಯಾಮೆರಾ ಪ್ರಾರಂಭಿಸಿ",
        cam_capture: "ಫೋಟೋ ತೆಗೆಯಿರಿ",
        cam_stop: "ನಿಲ್ಲಿಸಿ",
        
        selected_img: "ಆಯ್ಕೆಮಾಡಿದ ವಾಹನದ ಚಿತ್ರ",
        btn_run_assessment: "ತಪಾಸಣೆ ನಡೆಸಿ",
        
        loading_title: "ವಾಹನದ ಚಿತ್ರ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ",
        loading_sub: "AI ಮಾದರಿ ಮೌಲ್ಯಮಾಪನ ನಡೆಸುತ್ತಿದೆ...",
        step_uploading: "ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...",
        step_analyzing: "ಚಿತ್ರ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        step_running: "AI ಮಾದರಿ ಚಾಲನೆಯಲ್ಲಿದೆ...",
        step_generating: "ಫಲಿತಾಂಶ ಸಿದ್ಧಪಡಿಸಲಾಗುತ್ತಿದೆ...",
        
        res_header_tag: "ತಪಾಸಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ",
        res_header_title: "AI ಮುನ್ಸೂಚನೆ ಫಲಿತಾಂಶ",
        res_header_sub: "AI ಮಾದರಿಯಿಂದ ನಿಖರವಾದ ಬೈನರಿ ಫಲಿತಾಂಶ.",
        
        res_uploaded_img: "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರ",
        res_vehicle_status: "ವಾಹನದ ಪ್ರಸ್ತುತ ಸ್ಥಿತಿ",
        res_model_pred: "AI ಮಾದರಿ ಫಲಿತಾಂಶ",
        
        status_damaged: "ಹಾನಿಗೊಳಗಾಗಿದೆ (Damaged)",
        status_nodamage: "ಯಾವುದೇ ಹಾನಿ ಇಲ್ಲ (No Damage Detected)",
        
        summary_title: "AI ಸಾರಾಂಶ",
        summary_damaged_text: "AI ಮಾದರಿಯು ವಾಹನವು ಹಾನಿಗೊಳಗಾಗಿದೆ ಎಂದು ಸೂಚಿಸುವ ಗೋಚರ ಕುರುಹುಗಳನ್ನು ಪತ್ತೆ ಮಾಡಿದೆ. ಈ ಮುನ್ಸೂಚನೆಯು ಚಿತ್ರ ವಿಶ್ಲೇಷಣೆಯನ್ನು ಆಧರಿಸಿದೆ.",
        summary_nodamage_text: "ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರದಲ್ಲಿ AI ಮಾದರಿಯು ಯಾವುದೇ ಗೋಚರ ಹಾನಿಯನ್ನು ಪತ್ತೆ ಮಾಡಿಲ್ಲ.",
        
        btn_assess_another: "ಮತ್ತೊಂದು ಚಿತ್ರ ತಪಾಸಣೆ ಮಾಡಿ",
        btn_upload_new: "ಹೊಸ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        btn_return_home: "ಮುಖ್ಯ ಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ",
        btn_download_pdf: "ಫಲಿತಾಂಶವನ್ನು PDF ಆಗಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        
        history_tag: "ಸ್ಥಳೀಯ ದಾಖಲೆಗಳು",
        history_title: "ತಪಾಸಣೆ ಇತಿಹಾಸ",
        history_sub: "ನಿಮ್ಮ ಸೆಷನ್‌ನಿಂದ ಉಳಿಸಿದ ಮುನ್ಸೂಚನೆ ದಾಖಲೆಗಳು.",
        btn_clear_history: "ಇತಿಹಾಸ ಅಳಿಸಿ",
        history_empty: "ಇನ್ನೂ ಯಾವುದೇ ದಾಖಲೆಗಳು ಉಳಿಸಲ್ಪಟ್ಟಿಲ್ಲ. ಇತಿಹಾಸವನ್ನು ವೀಕ್ಷಿಸಲು ತಪಾಸಣೆ ಪೂರ್ಣಗೊಳಿಸಿ.",
        
        th_time: "ಸಮಯ",
        th_id: "ತಪಾಸಣೆ ID",
        th_status: "ವಾಹನದ ಸ್ಥಿತಿ",
        th_actions: "ಕ್ರಿಯೆಗಳು",
        
        footer_desc: "PyTorch Convolutional Neural Network ಬೈನರಿ ವರ್ಗೀಕರಣ ವ್ಯವಸ್ಥೆ.",
        
        // Chatbot Widget Translations (Kannada)
        chat_header: "AI ಕ್ಲೈಮ್‌ಗಳ ಸಹಾಯಕ",
        chat_sub: "ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ಪ್ರಶ್ನೆ ಕೇಳಿ",
        chat_faq_title: "ಸಾಮಾನ್ಯವಾಗಿ ಕೇಳಲಾಗುವ ಪ್ರಶ್ನೆಗಳು:",
        faq_1: "📋 ಕ್ಲೈಮ್‌ಗೆ ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು ಯಾವುವು?",
        faq_2: "⚠️ ವಾಹನ ಹಾನಿಗೊಳಗಾಗಿದ್ದರೆ ಮುಂದಿನ ಹಂತಗಳೇನು?",
        faq_3: "🤖 AI ಹಾನಿ ಪತ್ತೆ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ?",
        faq_4: "⏱️ ಕ್ಲೈಮ್ ಅನುಮೋದನೆಗೆ ಎಷ್ಟು ಸಮಯ ಬೇಕು?",
        chat_placeholder: "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಮೇಲಿನ ಪ್ರಶ್ನೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ...",
        chat_send: "ಕಳುಹಿಸಿ"
    }
};
