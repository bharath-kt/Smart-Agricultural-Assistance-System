r"""
MobileNetV2 Fine-Tuning Script for Tomato Leaf Disease Classification
Dataset: C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\tomato
Output: backend\ml_models\plant\tomato\tomato_disease_model.pth
Report: backend\ml_models\plant\tomato\evaluation_report.txt
"""

import os
import time
import copy
import json
import numpy as np
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

DATASET_ROOT = r"C:\Users\Admin\Desktop\Smart Agricultural Assistance System\dataset\tomato"
TRAIN_DIR = os.path.join(DATASET_ROOT, "train")
VALID_DIR = os.path.join(DATASET_ROOT, "valid")

MODEL_DIR = os.path.join("backend", "ml_models", "plant", "tomato")
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, "tomato_disease_model.pth")
BACKUP_SAVE_PATH = os.path.join(MODEL_DIR, "tomato_disease_model_backup.pth")
REPORT_SAVE_PATH = os.path.join(MODEL_DIR, "evaluation_report.txt")

EXPECTED_CLASSES = [
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

class SafeImageFolder(datasets.ImageFolder):
    """Custom ImageFolder handling extended-length Windows file paths (>260 chars)."""
    def __getitem__(self, index):
        path, target = self.samples[index]
        if os.name == 'nt' and not path.startswith('\\\\?\\'):
            safe_path = '\\\\?\\' + os.path.abspath(path)
        else:
            safe_path = path

        with open(safe_path, "rb") as f:
            sample = Image.open(f).convert("RGB")

        if self.transform is not None:
            sample = self.transform(sample)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return sample, target


def train_tomato_model():
    print("=" * 75)
    print("MOBILENETV2 END-TO-END FINE-TUNING FOR TOMATO DISEASE DETECTION")
    print("=" * 75)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using compute device: {device}")

    # Ensure backup of existing model before training
    if os.path.exists(MODEL_SAVE_PATH) and not os.path.exists(BACKUP_SAVE_PATH):
        import shutil
        shutil.copy2(MODEL_SAVE_PATH, BACKUP_SAVE_PATH)
        print(f"Created model backup at: {BACKUP_SAVE_PATH}")

    # 1. Image Transforms & Data Augmentations
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    valid_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    print("\nLoading datasets via SafeImageFolder...")
    train_dataset = SafeImageFolder(root=TRAIN_DIR, transform=train_transform)
    valid_dataset = SafeImageFolder(root=VALID_DIR, transform=valid_transform)

    print(f"Train Dataset: {len(train_dataset)} images across {len(train_dataset.classes)} classes.")
    print(f"Valid Dataset: {len(valid_dataset)} images across {len(valid_dataset.classes)} classes.")
    assert sorted(train_dataset.classes) == sorted(EXPECTED_CLASSES), "Class list mismatch!"

    class_to_idx = {c: i for i, c in enumerate(EXPECTED_CLASSES)}

    # Batch loaders
    batch_size = 64
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Class Weights for loss balancing
    train_targets = [y for _, y in train_dataset.samples]
    class_counts = np.bincount(train_targets, minlength=len(EXPECTED_CLASSES))
    weights = len(train_targets) / (len(EXPECTED_CLASSES) * class_counts)
    class_weights_tensor = torch.tensor(weights, dtype=torch.float).to(device)
    print("\nClass Weights:", {cls: round(w, 3) for cls, w in zip(EXPECTED_CLASSES, weights)})

    # 2. Build MobileNetV2 Model
    print("\nInitializing MobileNetV2 Architecture...")
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    in_features = model.classifier[1].in_features # 1280
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(256, len(EXPECTED_CLASSES))
    )
    model.to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)

    # STAGE 1: Warmup Classifier Head (Backbone Frozen)
    print("\n" + "-"*60)
    print("STAGE 1: WARMUP CLASSIFIER HEAD (3 EPOCHS)")
    print("-" * 60)
    for param in model.features.parameters():
        param.requires_grad = False

    optimizer_head = optim.AdamW(model.classifier.parameters(), lr=1e-3, weight_decay=1e-4)

    for epoch in range(1, 4):
        t0 = time.time()
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for imgs, lbls in train_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer_head.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, lbls)
            loss.backward()
            optimizer_head.step()

            running_loss += loss.item() * imgs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == lbls).sum().item()
            total += imgs.size(0)

        t_acc = correct / total
        t_loss = running_loss / total
        print(f"Warmup Epoch {epoch}/3 | Train Loss: {t_loss:.4f} Acc: {t_acc*100:.2f}% ({time.time()-t0:.1f}s)")

    # STAGE 2: Unfreeze Upper Backbone & Fine-Tune End-to-End
    print("\n" + "-"*60)
    print("STAGE 2: END-TO-END FINE-TUNING (UPPER BACKBONE + HEAD)")
    print("-" * 60)
    # Unfreeze upper feature blocks (features[10:])
    for param in model.features[10:].parameters():
        param.requires_grad = True

    # Differential learning rates: smaller lr for backbone, slightly larger for head
    optimizer = optim.AdamW([
        {'params': model.features[10:].parameters(), 'lr': 1e-4},
        {'params': model.classifier.parameters(), 'lr': 5e-4}
    ], weight_decay=1e-4)

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=2)

    best_val_acc = 0.0
    best_train_acc = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())
    patience = 6
    patience_counter = 0

    max_epochs = 15
    for epoch in range(1, max_epochs + 1):
        t0 = time.time()

        # Training Phase
        model.train()
        train_loss, train_correct, train_total = 0.0, 0, 0
        for i, (imgs, lbls) in enumerate(train_loader):
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, lbls)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * imgs.size(0)
            _, preds = torch.max(outputs, 1)
            train_correct += (preds == lbls).sum().item()
            train_total += imgs.size(0)

        epoch_train_loss = train_loss / train_total
        epoch_train_acc = train_correct / train_total

        # Validation Phase
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for imgs, lbls in valid_loader:
                imgs, lbls = imgs.to(device), lbls.to(device)
                outputs = model(imgs)
                loss = criterion(outputs, lbls)
                val_loss += loss.item() * imgs.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == lbls).sum().item()
                val_total += imgs.size(0)

        epoch_val_loss = val_loss / val_total
        epoch_val_acc = val_correct / val_total

        scheduler.step(epoch_val_acc)

        print(f"Epoch {epoch:2d}/{max_epochs} | Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc*100:.2f}% | Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc*100:.2f}% ({time.time()-t0:.1f}s)")

        # Save Checkpoint if Validation Accuracy improves
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            best_train_acc = epoch_train_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            patience_counter = 0

            # Save to disk immediately
            os.makedirs(MODEL_DIR, exist_ok=True)
            torch.save({
                'model_state_dict': best_model_wts,
                'classes': EXPECTED_CLASSES,
                'class_to_idx': class_to_idx,
                'val_acc': float(best_val_acc),
                'train_acc': float(best_train_acc)
            }, MODEL_SAVE_PATH)
            print(f"  --> NEW BEST VAL ACCURACY: {best_val_acc*100:.2f}%! Saved model checkpoint.")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\nEarly stopping triggered after {patience} epochs without improvement.")
                break

    print(f"\nFine-Tuning Complete! Best Validation Accuracy: {best_val_acc*100:.2f}%")

    # Load Best Model Weights for Final Evaluation
    model.load_state_dict(best_model_wts)
    model.eval()

    # 3. Final Evaluation & Report Generation
    print("\n" + "=" * 60)
    print("EVALUATING IMPROVED MODEL ON VALIDATION SET")
    print("=" * 60)

    val_preds_list, val_targets_list = [], []
    with torch.no_grad():
        for imgs, lbls in valid_loader:
            imgs = imgs.to(device)
            outputs = model(imgs)
            _, preds = torch.max(outputs, 1)
            val_preds_list.extend(preds.cpu().numpy())
            val_targets_list.extend(lbls.numpy())

    report_str = classification_report(val_targets_list, val_preds_list, target_names=EXPECTED_CLASSES, digits=4)
    cm = confusion_matrix(val_targets_list, val_preds_list)

    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(val_targets_list, val_preds_list, average='macro')
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(val_targets_list, val_preds_list, average='weighted')
    per_class_p, per_class_r, per_class_f1, per_class_supp = precision_recall_fscore_support(val_targets_list, val_preds_list, average=None)

    # Per-class accuracies
    cm_diag = cm.diagonal()
    cm_sum = cm.sum(axis=1)
    per_class_acc = np.divide(cm_diag, cm_sum, out=np.zeros_like(cm_diag, dtype=float), where=cm_sum!=0)

    print("\nClassification Report:\n", report_str)
    print("\nConfusion Matrix:\n", cm)

    with open(REPORT_SAVE_PATH, "w") as f:
        f.write("IMPROVED TOMATO LEAF DISEASE CLASSIFICATION EVALUATION REPORT (MobileNetV2 Fine-Tuned)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Framework: PyTorch (MobileNetV2 Fine-Tuning)\n")
        f.write(f"Training Accuracy: {best_train_acc*100:.2f}%\n")
        f.write(f"Validation Accuracy: {best_val_acc*100:.2f}%\n")
        f.write(f"Macro Precision: {macro_p*100:.2f}%\n")
        f.write(f"Macro Recall: {macro_r*100:.2f}%\n")
        f.write(f"Macro F1-Score: {macro_f1*100:.2f}%\n")
        f.write(f"Weighted F1-Score: {weighted_f1*100:.2f}%\n\n")

        f.write("Per-Class Metrics:\n")
        f.write(f"{'Class Name':<40} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}\n")
        f.write("-" * 90 + "\n")
        for idx, cls_name in enumerate(EXPECTED_CLASSES):
            f.write(f"{cls_name:<40} | {per_class_acc[idx]*100:<9.2f}% | {per_class_p[idx]*100:<9.2f}% | {per_class_r[idx]*100:<9.2f}% | {per_class_f1[idx]*100:<9.2f}%\n")

        f.write("\nClassification Report:\n" + report_str + "\n\n")
        f.write("Confusion Matrix:\n" + np.array2string(cm, separator=', ') + "\n")

    print(f"\nEvaluation Report successfully saved to: {REPORT_SAVE_PATH}")

if __name__ == "__main__":
    train_tomato_model()
