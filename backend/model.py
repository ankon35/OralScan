from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F
import os

# 1. Setup Model (Correct Spelling)
model_id = "ankon1/oral-cancer-classifer"
subfolder_name = "vit_model_directory"

print(f"Loading model: {model_id}...")

try:
    # 2. Load Model
    processor = AutoImageProcessor.from_pretrained(model_id, subfolder=subfolder_name)
    model = AutoModelForImageClassification.from_pretrained(model_id, subfolder=subfolder_name)
    
    # 3. Load Image (Use forward slash for Windows paths)
    image_path = "backend/test-image.jpeg" 
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Could not find image at '{image_path}'")
        exit()

    image = Image.open(image_path).convert("RGB")

    # 4. Predict
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # 5. Get Raw Result
    predicted_class_idx = logits.argmax(-1).item()
    raw_label = model.config.id2label[predicted_class_idx] # Returns "LABEL_0" or "LABEL_1"
    
    # Calculate Confidence
    probs = F.softmax(logits, dim=-1)
    confidence = probs[0][predicted_class_idx].item() * 100

    # =========================================================
    # 6. CUSTOM LABEL MAPPING (The fix you asked for)
    # =========================================================
    
    if raw_label == "LABEL_1":
        final_result = "⚠️ Cancer Positive"
    elif raw_label == "LABEL_0":
        final_result = "✅ Cancer Negative"
    else:
        # Fallback if the model changes in future
        final_result = f"Unknown Label ({raw_label})"

    # 7. Print Report
    print("\n" + "="*40)
    print("DIAGNOSIS REPORT")
    print("="*40)
    print(f"Prediction : {final_result}")
    print(f"Confidence : {confidence:.2f}%")
    print("="*40 + "\n")

except Exception as e:
    print(f"Error: {e}")