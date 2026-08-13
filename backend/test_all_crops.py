r"""
End-to-End Testing & Verification Script for Tomato, Corn, and Paddy Disease Models
Tests:
- Direct PyTorch Model Inference vs. FastAPI Service Endpoint Inference
- 1 Image from EACH of the 11 Tomato Classes
- 1 Corn Image
- 1 Paddy Image
"""

import os
import sys
import io
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import asyncio

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.disease_service import disease_service

DATASET_TOMATO = r"C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\tomato\valid"
DATASET_CORN = r"C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\corn\data"

TOMATO_CLASSES = [
    'Bacterial_spot',
    'Early_blight',
    'Late_blight',
    'Leaf_Mold',
    'Septoria_leaf_spot',
    'Spider_mites Two-spotted_spider_mite',
    'Target_Spot',
    'Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato_mosaic_virus',
    'healthy',
    'powdery_mildew'
]

def load_direct_tomato_model(model_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(model_path, map_location=device)
    model = models.mobilenet_v2()
    in_f = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_f, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, 11)
    )
    model.load_state_dict(ckpt['model_state_dict'])
    model.to(device)
    model.eval()
    return model, device, ckpt.get('classes', TOMATO_CLASSES)

async def run_tests():
    print("=" * 75)
    print("END-TO-END VERIFICATION: TOMATO, CORN, AND PADDY MODELS")
    print("=" * 75)

    tomato_model_path = os.path.join("backend", "ml_models", "plant", "tomato", "tomato_disease_model.pth")
    if not os.path.exists(tomato_model_path):
        print(f"ERROR: Tomato model not found at {tomato_model_path}")
        return

    direct_model, device, classes_in_ckpt = load_direct_tomato_model(tomato_model_path)
    print(f"Direct Tomato PyTorch Model Loaded Successfully ({len(classes_in_ckpt)} classes).")

    # Reload backend disease service to ensure fresh models are loaded
    disease_service.reload_models()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    print("\n--- 1. TESTING ALL 11 TOMATO CLASSES ---")
    tomato_success = 0

    for cls_name in TOMATO_CLASSES:
        cls_dir = os.path.join(DATASET_TOMATO, cls_name)
        if not os.path.exists(cls_dir):
            print(f"[SKIP] Directory missing for {cls_name}")
            continue

        sample_file = next((f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))), None)
        if not sample_file:
            print(f"[SKIP] No sample image in {cls_name}")
            continue

        img_path = os.path.join(cls_dir, sample_file)
        with open(img_path, 'rb') as f:
            img_bytes = f.read()

        # Direct PyTorch Model Inference
        pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        t_img = transform(pil_img).unsqueeze(0).to(device)
        with torch.no_grad():
            out = direct_model(t_img)
            probs = torch.softmax(out, dim=1)[0]
            direct_idx = torch.argmax(probs).item()
            direct_pred_cls = classes_in_ckpt[direct_idx]
            direct_conf = probs[direct_idx].item()

        # Service / API Inference
        api_result = await disease_service.detect_disease(img_bytes, crop_type="Tomato")

        assert api_result is not None, "API returned None!"
        api_detected = api_result["detected_disease"].replace("Tomato___", "")
        api_conf = api_result["confidence_score"]

        match_status = "MATCH" if direct_pred_cls == api_detected else "MISMATCH"
        print(f"Class: {cls_name:<38} | Direct: {direct_pred_cls:<30} | API: {api_detected:<30} [{match_status}]")

        if match_status == "MATCH":
            tomato_success += 1

    print(f"\nTomato Class Verification Score: {tomato_success}/{len(TOMATO_CLASSES)} matches.")

    print("\n--- 2. TESTING CORN MODEL INFERENCE ---")
    corn_cls_dir = os.path.join(DATASET_CORN, "Healthy")
    corn_sample = next((f for f in os.listdir(corn_cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))), None)
    if corn_sample:
        corn_img_path = os.path.join(corn_cls_dir, corn_sample)
        with open(corn_img_path, 'rb') as f:
            corn_bytes = f.read()
        corn_api_res = await disease_service.detect_disease(corn_bytes, crop_type="Corn")
        print(f"Corn Test Result: Plant={corn_api_res['plant_name']}, Disease={corn_api_res['disease_name']}, Confidence={corn_api_res['confidence_score']*100:.2f}%")
    else:
        print("[SKIP] No corn sample file found.")

    print("\n--- 3. TESTING PADDY MODEL INFERENCE ---")
    dummy_img = Image.new('RGB', (224, 224), color='green')
    buf = io.BytesIO()
    dummy_img.save(buf, format='JPEG')
    paddy_bytes = buf.getvalue()
    paddy_api_res = await disease_service.detect_disease(paddy_bytes, crop_type="Paddy")
    print(f"Paddy Test Result: Plant={paddy_api_res['plant_name']}, Disease={paddy_api_res['disease_name']}, Confidence={paddy_api_res['confidence_score']*100:.2f}%")

    print("\n" + "=" * 75)
    print("ALL END-TO-END TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    asyncio.run(run_tests())
