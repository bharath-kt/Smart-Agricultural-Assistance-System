"""
Inference Verification Script for Trained Corn Leaf Disease Model
"""

import os
import random
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn

MODEL_PATH = os.path.join("backend", "ml_models", "plant_disease_model.pth")
DATASET_DIR = r"C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\corn\data"
CLASSES = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']

class CornCNNModel(nn.Module):
    def __init__(self, num_classes=4):
        super(CornCNNModel, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(128 * 4 * 4, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def test_inference():
    print("="*60)
    print("TESTING TRAINED CORN LEAF DISEASE MODEL INFERENCE")
    print("="*60)

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading PyTorch model from: {MODEL_PATH}")
    checkpoint = torch.load(MODEL_PATH, map_location=device)

    model = CornCNNModel(num_classes=4)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    print(f"Model loaded successfully! Validation Accuracy: {checkpoint.get('val_acc', 0)*100:.2f}%")

    print("\nRunning inference on 8 random test images...")
    correct_predictions = 0
    total_tested = 0

    for true_class in CLASSES:
        class_dir = os.path.join(DATASET_DIR, true_class)
        if not os.path.exists(class_dir):
            continue

        sample_files = random.sample(os.listdir(class_dir), min(2, len(os.listdir(class_dir))))
        for fname in sample_files:
            fpath = os.path.join(class_dir, fname)

            img = cv2.imread(fpath)
            if img is None:
                continue
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (128, 128))
            img = img.astype(np.float32) / 255.0
            img = (img - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
            img_tensor = torch.tensor(np.transpose(img, (2, 0, 1)), dtype=torch.float32).unsqueeze(0).to(device)

            with torch.no_grad():
                outputs = model(img_tensor)
                probs = torch.softmax(outputs, dim=1)[0]
                pred_idx = torch.argmax(probs).item()
                pred_class = CLASSES[pred_idx]
                confidence = probs[pred_idx].item()

            is_correct = (pred_class == true_class)
            if is_correct:
                correct_predictions += 1
            total_tested += 1

            status = "OK" if is_correct else "MISMATCH"
            print(f"[{status}] True: {true_class:<15} | Pred: {pred_class:<15} | Confidence: {confidence*100:.2f}%")

    print("\n" + "="*60)
    print(f"Sample Test Accuracy: {correct_predictions}/{total_tested} ({correct_predictions/total_tested*100:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    test_inference()
