from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F
import os

# --- 1. SETUP MODEL ---
model_id = "ankon1/oral-cancer-classifer" 
subfolder_name = "vit_model_directory"

print(f"Loading model: {model_id}...")

try:
    # Load the Processor (This handles resizing and normalization automatically)
    processor = AutoImageProcessor.from_pretrained(model_id, subfolder=subfolder_name)
    model = AutoModelForImageClassification.from_pretrained(model_id, subfolder=subfolder_name)

    # --- 2. DEFINE PREPROCESSING FUNCTION ---
    def preprocess_image(image_path, model_processor):
        """
        This function replaces the manual 'load_img' and 'img_to_array' code.
        It opens the image, converts to RGB, resizes it, and normalizes it
        exactly how the AI model expects.
        """
        if not os.path.exists(image_path):
            print(f"❌ Error: Could not find image at '{image_path}'")
            exit()
            
        # 1. Open Image (Equivalent to load_img)
        img = Image.open(image_path).convert("RGB")
        
        # 2. Process (Equivalent to img_to_array + normalization + resizing)
        # The processor reads the model config to know the exact target size (e.g., 224x224)
        input_tensor = model_processor(images=img, return_tensors="pt")
        
        return input_tensor

    # --- 3. RUN THE PROCESS ---
    
    # Path to your image
    image_path = "backend/test-image.jpeg" 

    # A. Preprocess the image
    print("Preprocessing image...")
    inputs = preprocess_image(image_path, processor)

    # B. Put in the model (Inference)
    print("Analyzing...")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # --- 4. INTERPRET RESULTS ---
    
    predicted_class_idx = logits.argmax(-1).item()
    raw_label = model.config.id2label[predicted_class_idx] # "LABEL_0" or "LABEL_1"
    
    # Calculate Confidence
    probs = F.softmax(logits, dim=-1)
    confidence = probs[0][predicted_class_idx].item() * 100

    # --- 5. CUSTOM LABEL MAPPING ---
    # LABEL_0 is usually Negative (Healthy), LABEL_1 is Positive (Cancer)
    if raw_label == "LABEL_1":
        final_result = "⚠️ Cancer Positive"
    elif raw_label == "LABEL_0":
        final_result = "✅ Cancer Negative"
    else:
        final_result = f"Unknown Label ({raw_label})"

    # --- 6. PRINT REPORT ---
    print("\n" + "="*40)
    print("DIAGNOSIS REPORT")
    print("="*40)
    print(f"Prediction : {final_result}")
    print(f"Confidence : {confidence:.2f}%")
    print("="*40 + "\n")

except Exception as e:
    print(f"Error: {e}")