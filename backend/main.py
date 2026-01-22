from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F
import io

app = FastAPI(title="Oral Cancer Detection API")

# Enable CORS so your UI can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. MODEL SETUP ---
# Corrected spelling: 'classifier'
MODEL_ID = "ankon1/oral-cancer-classifer"
SUBFOLDER = "vit_model_directory"

print(f"Loading model: {MODEL_ID} from folder {SUBFOLDER}...")

try:
    # The processor handles the specific preprocessing (resizing, normalization) needed for this model
    processor = AutoImageProcessor.from_pretrained(MODEL_ID, subfolder=SUBFOLDER)
    model = AutoModelForImageClassification.from_pretrained(MODEL_ID, subfolder=SUBFOLDER)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Tip: Check internet connection or folder name.")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    # 1. Validate File Type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 2. Read and Convert Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # 3. Preprocess (Auto-resize & Normalize)
        inputs = processor(images=image, return_tensors="pt")

        # 4. Inference
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        # 5. Extract Data
        predicted_idx = logits.argmax(-1).item()
        raw_label = model.config.id2label[predicted_idx] # Gets "LABEL_0" or "LABEL_1"
        
        # Calculate Confidence
        probs = F.softmax(logits, dim=-1)
        confidence_score = probs[0][predicted_idx].item() * 100

        # 6. Map Logic: Label -> Readable Result
        if raw_label == "LABEL_1":
            final_result = "Cancer Positive"
        elif raw_label == "LABEL_0":
            final_result = "Cancer Negative"
        else:
            final_result = f"Unknown ({raw_label})"

        # 7. Return JSON
        return {
            "result": final_result,
            "confidence": round(confidence_score, 2),
            "raw_label": raw_label  # Included for debugging purposes
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
def home():
    return {"message": "Oral Cancer Detection API is running"}