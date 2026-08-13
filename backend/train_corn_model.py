r"""
MobileNetV2 Fast Feature Training & Verification Script for Corn Leaf Disease
Dataset: C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\corn\data
Model Output: backend\ml_models\plant_disease_model.pth
"""

import os
import time
import copy
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets, transforms, models

DATASET_DIR = r"C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\corn\data"
MODEL_SAVE_PATH = os.path.join("backend", "ml_models", "plant_disease_model.pth")
REPORT_SAVE_PATH = os.path.join("backend", "ml_models", "evaluation_report.txt")
EXPECTED_CLASSES = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']

def train_model():
    print("="*60)
    print("STARTING MOBILENETV2 FAST FEATURE TRAINING")
    print("="*60)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Standard ImageNet Transforms
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    print("Loading dataset via ImageFolder...")
    dataset_raw = datasets.ImageFolder(root=DATASET_DIR, transform=transform)
    print("Folder classes:", dataset_raw.classes)

    class_to_idx = {c: i for i, c in enumerate(EXPECTED_CLASSES)}
    targets = [class_to_idx[dataset_raw.classes[label]] for _, label in dataset_raw.samples]

    indices = np.arange(len(dataset_raw))
    from sklearn.model_selection import train_test_split
    train_idx, temp_idx, _, temp_targets = train_test_split(indices, targets, test_size=0.20, random_state=42, stratify=targets)
    val_idx, test_idx, _, _ = train_test_split(temp_idx, temp_targets, test_size=0.50, random_state=42, stratify=temp_targets)

    print(f"Splits -> Train: {len(train_idx)}, Val: {len(val_idx)}, Test: {len(test_idx)}")

    # Class Weights for balancing
    train_targets_arr = np.array([targets[i] for i in train_idx])
    class_counts = np.bincount(train_targets_arr)
    weights = len(train_targets_arr) / (len(EXPECTED_CLASSES) * class_counts)
    class_weights_tensor = torch.tensor(weights, dtype=torch.float).to(device)
    print(f"Class Weights: {dict(zip(EXPECTED_CLASSES, np.round(weights, 3)))}")

    # Extract 1280-dim feature vectors using MobileNetV2
    print("\nExtracting MobileNetV2 1280-dim feature vectors...")
    backbone = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    backbone.classifier = nn.Identity()
    backbone.to(device)
    backbone.eval()

    def get_features(subset_indices):
        subset = torch.utils.data.Subset(dataset_raw, subset_indices)
        loader = DataLoader(subset, batch_size=64, shuffle=False, num_workers=0)
        feats, lbls = [], []
        with torch.no_grad():
            for imgs, raw_lbls in loader:
                imgs = imgs.to(device)
                mapped_lbls = torch.tensor([class_to_idx[dataset_raw.classes[l.item()]] for l in raw_lbls], dtype=torch.long)
                f = backbone(imgs)
                feats.append(f.cpu())
                lbls.append(mapped_lbls)
        return torch.cat(feats, dim=0), torch.cat(lbls, dim=0)

    t0 = time.time()
    train_feat, train_target = get_features(train_idx)
    val_feat, val_target = get_features(val_idx)
    test_feat, test_target = get_features(test_idx)
    print(f"Feature extraction complete in {time.time() - t0:.2f}s!")

    # Classifier Head
    classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(1280, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, len(EXPECTED_CLASSES))
    ).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = optim.Adam(classifier.parameters(), lr=2e-3, weight_decay=1e-4)

    print("\nTraining Classifier Head (40 Epochs)...")
    train_feat_dev, train_target_dev = train_feat.to(device), train_target.to(device)
    val_feat_dev, val_target_dev = val_feat.to(device), val_target.to(device)

    best_val_acc = 0.0
    best_classifier_state = None

    for epoch in range(40):
        classifier.train()
        optimizer.zero_grad()
        outputs = classifier(train_feat_dev)
        loss = criterion(outputs, train_target_dev)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        train_acc = (preds == train_target_dev).float().mean().item()

        classifier.eval()
        with torch.no_grad():
            val_outputs = classifier(val_feat_dev)
            val_loss = criterion(val_outputs, val_target_dev).item()
            _, val_preds = torch.max(val_outputs, 1)
            val_acc = (val_preds == val_target_dev).float().mean().item()

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            best_classifier_state = copy.deepcopy(classifier.state_dict())

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:2d}/40 | Train Loss: {loss.item():.4f} Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")

    print(f"\nClassifier Head Training Complete! Best Val Acc: {best_val_acc*100:.2f}%")

    # Assemble & Verify Full Model
    full_model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    in_features = full_model.classifier[1].in_features
    full_model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, len(EXPECTED_CLASSES))
    )
    classifier.load_state_dict(best_classifier_state)
    full_model.classifier = classifier
    full_model.to(device)
    full_model.eval()

    # Save Checkpoint
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    torch.save({
        'model_state_dict': full_model.state_dict(),
        'classes': EXPECTED_CLASSES,
        'val_acc': float(best_val_acc)
    }, MODEL_SAVE_PATH)
    print(f"\nModel saved to: {MODEL_SAVE_PATH}")

    # Evaluate Full Model on Test Set
    print("\n" + "="*50)
    print("EVALUATING FULL MODEL ON TEST SET")
    print("="*50)

    test_subset = torch.utils.data.Subset(dataset_raw, test_idx)
    test_loader = DataLoader(test_subset, batch_size=32, shuffle=False, num_workers=0)

    all_preds, all_targets = [], []
    with torch.no_grad():
        for imgs, raw_lbls in test_loader:
            imgs = imgs.to(device)
            mapped_lbls = [class_to_idx[dataset_raw.classes[l.item()]] for l in raw_lbls]
            outputs = full_model(imgs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(mapped_lbls)

    report = classification_report(all_targets, all_preds, target_names=EXPECTED_CLASSES, digits=4)
    cm = confusion_matrix(all_targets, all_preds)

    print("\nClassification Report:\n", report)
    print("\nConfusion Matrix:\n", cm)

    with open(REPORT_SAVE_PATH, "w") as f:
        f.write("CORN LEAF DISEASE CLASSIFICATION EVALUATION REPORT (MobileNetV2)\n")
        f.write("="*60 + "\n\n")
        f.write("Classes: " + ", ".join(EXPECTED_CLASSES) + "\n\n")
        f.write(f"Validation Accuracy: {best_val_acc*100:.2f}%\n\n")
        f.write("Classification Report:\n" + report + "\n\n")
        f.write("Confusion Matrix:\n" + str(cm) + "\n")

    print(f"\nReport saved to: {REPORT_SAVE_PATH}")

if __name__ == "__main__":
    train_model()
