from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import torch.nn.functional as F
import io

app = FastAPI(title="Oral Cancer Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. FIXED MODEL LOADING ---
# Correct spelling: 'classifier' instead of 'classifer'
MODEL_ID = "ankon1/oral-cancer-classiferr" 
SUBFOLDER = "vit_model_directory"  # Required because your files are in this folder

print(f"Loading model: {MODEL_ID} from folder {SUBFOLDER}...")

try:
    # We must pass the 'subfolder' argument so it finds the files inside 'vit_model_directory'
    processor = AutoImageProcessor.from_pretrained(MODEL_ID, subfolder=SUBFOLDER)
    model = AutoModelForImageClassification.from_pretrained(MODEL_ID, subfolder=SUBFOLDER)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Check if the repository is private or if the folder name matches exactly.")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        predicted_idx = logits.argmax(-1).item()
        predicted_label = model.config.id2label[predicted_idx]
        
        probs = F.softmax(logits, dim=-1)
        confidence_score = probs[0][predicted_idx].item() * 100

        return {
            "result": predicted_label,
            "confidence": round(confidence_score, 2)
        }

    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during prediction")

@app.get("/")
def home():
    return {"message": "Oral Cancer Detection API is running"}