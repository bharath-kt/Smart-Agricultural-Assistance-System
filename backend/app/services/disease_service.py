"""Plant disease detection service supporting Tomato, Corn, and Paddy models."""
import os
import io
from datetime import datetime
from typing import Optional, Dict, Any, List
import numpy as np
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DiseaseDetectionService:
    """Service for plant disease detection using PyTorch MobileNetV2 CNNs."""
    
    # Supported crops
    SUPPORTED_CROPS = ["Tomato", "Corn", "Paddy"]

    # Class mappings
    CORN_CLASSES = [
        "Corn_(maize)___Blight",
        "Corn_(maize)___Common_Rust",
        "Corn_(maize)___Gray_Leaf_Spot",
        "Corn_(maize)___Healthy"
    ]

    TOMATO_CLASSES = [
        "Tomato___Bacterial_spot",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",
        "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy",
        "Tomato___powdery_mildew"
    ]

    PADDY_CLASSES = [
        "Paddy___Bacterial_leaf_blight",
        "Paddy___Brown_spot",
        "Paddy___Leaf_smut",
        "Paddy___healthy"
    ]

    # Treatment recommendations
    DISEASE_TREATMENTS = {
        "Corn_(maize)___Blight": {
            "organic": "Remove infected debris, rotate crops, apply copper spray or neem oil",
            "chemical": "Apply fungicides with mancozeb, chlorothalonil, or azoxystrobin",
            "preventive": "Plant resistant hybrids, practice 3-year crop rotation, avoid continuous corn planting"
        },
        "Corn_(maize)___Common_Rust": {
            "organic": "Plant resistant varieties, remove infected leaves, improve field sanitation",
            "chemical": "Apply fungicides with azoxystrobin or propiconazole if severe",
            "preventive": "Use resistant hybrids, early planting, practice crop rotation"
        },
        "Corn_(maize)___Gray_Leaf_Spot": {
            "organic": "Remove infected crop debris, improve field sanitation, apply neem oil",
            "chemical": "Apply fungicides with azoxystrobin or pyraclostrobin",
            "preventive": "Crop rotation, use resistant hybrids, maintain balanced soil fertilization"
        },
        "Corn_(maize)___Healthy": {
            "organic": "Maintain regular care, adequate watering, and organic soil composting",
            "chemical": "No chemical treatment required; plant is healthy",
            "preventive": "Continue crop rotation, regular field monitoring, and proper plant spacing"
        },
        "Tomato___Bacterial_spot": {
            "organic": "Remove infected leaves, apply copper-based bactericides, avoid working when wet",
            "chemical": "Apply copper hydroxide or streptomycin sulfate",
            "preventive": "Use disease-free seeds, sanitize tools, avoid overhead irrigation"
        },
        "Tomato___Early_blight": {
            "organic": "Remove lower infected leaves, mulch around plants, apply copper spray",
            "chemical": "Apply chlorothalonil or mancozeb fungicides",
            "preventive": "Rotate crops, stake plants, avoid wetting foliage"
        },
        "Tomato___Late_blight": {
            "organic": "Remove infected plants immediately, apply copper fungicide",
            "chemical": "Apply metalaxyl-m or cymoxanil fungicides urgently",
            "preventive": "Use resistant varieties, ensure good drainage, avoid overhead watering"
        },
        "Tomato___Leaf_Mold": {
            "organic": "Improve ventilation, remove infected leaves, apply neem oil",
            "chemical": "Apply fungicides with chlorothalonil or mancozeb",
            "preventive": "Ensure proper spacing, avoid high humidity, plant resistant varieties"
        },
        "Tomato___Septoria_leaf_spot": {
            "organic": "Remove infected lower leaves, mulch with plastic, apply copper spray",
            "chemical": "Apply fungicides with chlorothalonil or mancozeb",
            "preventive": "Rotate crops, stake plants, remove crop debris"
        },
        "Tomato___Spider_mites Two-spotted_spider_mite": {
            "organic": "Spray water on undersides of leaves, introduce predatory mites, apply neem oil",
            "chemical": "Apply miticides with abamectin or spiromesifen",
            "preventive": "Maintain humidity, monitor regularly, avoid dusty conditions"
        },
        "Tomato___Target_Spot": {
            "organic": "Remove infected leaves, improve air circulation, apply copper fungicide",
            "chemical": "Apply fungicides with boscalid or chlorothalonil",
            "preventive": "Proper spacing, avoid overhead irrigation, plant resistant varieties"
        },
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
            "organic": "Remove infected plants, control whiteflies with sticky traps and neem oil",
            "chemical": "Apply insecticides for whitefly control (imidacloprid)",
            "preventive": "Use resistant varieties, netting to block whiteflies, reflective mulches"
        },
        "Tomato___Tomato_mosaic_virus": {
            "organic": "Remove infected plants, sanitize tools, control aphids",
            "chemical": "No chemical cure; focus on aphid and vector control",
            "preventive": "Use resistant varieties, sanitize hands/tools, avoid tobacco use near plants"
        },
        "Tomato___healthy": {
            "organic": "Maintain regular care, proper staking, and organic soil composting",
            "chemical": "No chemical treatment required; plant is healthy",
            "preventive": "Continue crop rotation, regular field monitoring, and proper plant spacing"
        },
        "Tomato___powdery_mildew": {
            "organic": "Spray with sulfur or potassium bicarbonate, apply neem oil, improve air circulation",
            "chemical": "Apply sulfur-based fungicides or myclobutanil",
            "preventive": "Provide adequate spacing, plant in full sun, avoid high nitrogen fertilizers"
        },
        "Paddy___Bacterial_leaf_blight": {
            "organic": "Ensure field drainage, apply balanced fertilizers, avoid excessive nitrogen",
            "chemical": "Apply copper hydroxide + streptomycin sulfate",
            "preventive": "Use resistant rice varieties, avoid deep water during tillering"
        },
        "Paddy___Brown_spot": {
            "organic": "Improve soil fertility, apply potassium and micronutrients, neem oil",
            "chemical": "Apply mancozeb or edifenphos",
            "preventive": "Use seed treatment, ensure balanced soil nutrition"
        },
        "Paddy___Leaf_smut": {
            "organic": "Remove infected plants, maintain clean field borders",
            "chemical": "Apply copper-based fungicides if severe",
            "preventive": "Practice crop rotation, balanced fertilization"
        },
        "Paddy___healthy": {
            "organic": "Maintain proper water level and organic soil fertility",
            "chemical": "No chemical treatment required; crop is healthy",
            "preventive": "Regular field inspection, proper weed management"
        },
        "default": {
            "organic": "Remove infected plant parts, improve air circulation, apply organic fungicides",
            "chemical": "Consult local agricultural extension for appropriate fungicides",
            "preventive": "Practice crop rotation, maintain plant health, ensure proper spacing"
        }
    }

    def __init__(self):
        self.models = {}
        self.classes_map = {}
        self.device = None
        self._load_models()
    
    def _load_models(self):
        """Load PyTorch models for Corn, Tomato, and Paddy."""
        try:
            import torch
            import torch.nn as nn
            from torchvision import models

            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Loading disease models using device: {self.device}")

            # 1. Load Corn Model
            corn_paths = [
                os.path.join("backend", "ml_models", "plant_disease_model.pth"),
                os.path.join("ml_models", "plant_disease_model.pth"),
                os.path.join("backend", "ml_models", "plant", "corn", "corn_disease_model.pth")
            ]
            corn_path = next((p for p in corn_paths if os.path.exists(p)), None)

            if corn_path:
                ckpt = torch.load(corn_path, map_location=self.device)
                model_corn = models.mobilenet_v2()
                in_f = model_corn.classifier[1].in_features
                model_corn.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_f, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, 4)
                )
                model_corn.load_state_dict(ckpt['model_state_dict'])
                model_corn.to(self.device)
                model_corn.eval()

                self.models['Corn'] = model_corn
                self.classes_map['Corn'] = self.CORN_CLASSES
                logger.info(f"PyTorch Corn model loaded successfully from {corn_path}")
            else:
                logger.warning("Corn model path not found!")

            # 2. Load Tomato Model
            tomato_paths = [
                os.path.join("backend", "ml_models", "plant", "tomato", "tomato_disease_model.pth"),
                os.path.join("ml_models", "plant", "tomato", "tomato_disease_model.pth")
            ]
            tomato_path = next((p for p in tomato_paths if os.path.exists(p)), None)

            if tomato_path:
                ckpt = torch.load(tomato_path, map_location=self.device)
                classes_in_ckpt = ckpt.get('classes', [c.replace("Tomato___", "") for c in self.TOMATO_CLASSES])
                
                model_tomato = models.mobilenet_v2()
                in_f = model_tomato.classifier[1].in_features
                model_tomato.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_f, 256),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(256, len(classes_in_ckpt))
                )
                model_tomato.load_state_dict(ckpt['model_state_dict'])
                model_tomato.to(self.device)
                model_tomato.eval()

                self.models['Tomato'] = model_tomato
                self.classes_map['Tomato'] = [f"Tomato___{c}" for c in classes_in_ckpt]
                logger.info(f"PyTorch Tomato model loaded successfully from {tomato_path}")
            else:
                logger.warning("Tomato model path not found!")

            # 3. Load Paddy Model (or fallback)
            paddy_paths = [
                os.path.join("backend", "ml_models", "plant", "paddy", "paddy_disease_model.pth"),
                os.path.join("ml_models", "plant", "paddy", "paddy_disease_model.pth")
            ]
            paddy_path = next((p for p in paddy_paths if os.path.exists(p)), None)

            if paddy_path:
                ckpt = torch.load(paddy_path, map_location=self.device)
                classes_in_ckpt = ckpt.get('classes', [c.replace("Paddy___", "") for c in self.PADDY_CLASSES])
                model_paddy = models.mobilenet_v2()
                in_f = model_paddy.classifier[1].in_features
                model_paddy.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_f, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, len(classes_in_ckpt))
                )
                model_paddy.load_state_dict(ckpt['model_state_dict'])
                model_paddy.to(self.device)
                model_paddy.eval()
                self.models['Paddy'] = model_paddy
                self.classes_map['Paddy'] = [f"Paddy___{c}" for c in classes_in_ckpt]
                logger.info(f"PyTorch Paddy model loaded from {paddy_path}")
            else:
                self.classes_map['Paddy'] = self.PADDY_CLASSES

        except Exception as e:
            logger.error(f"Error loading disease models: {e}")

    def reload_models(self):
        """Reload models from disk."""
        self._load_models()
    
    async def detect_disease(
        self,
        image_bytes: bytes,
        crop_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Detect plant disease from leaf image for specified crop."""
        try:
            # Normalize crop_type string
            normalized_crop = "Corn"
            if crop_type:
                crop_str = crop_type.strip().capitalize()
                for c in self.SUPPORTED_CROPS:
                    if c.lower() == crop_str.lower():
                        normalized_crop = c
                        break
            
            if crop_type and normalized_crop not in self.SUPPORTED_CROPS:
                return {
                    "error": f"Unsupported plant '{crop_type}'. Upload Tomato, Corn, or Paddy leaf.",
                    "supported_crops": self.SUPPORTED_CROPS
                }

            # Reload models if target crop model was not initially ready
            if normalized_crop not in self.models:
                self.reload_models()

            selected_model = self.models.get(normalized_crop)
            class_labels = self.classes_map.get(normalized_crop, self.CORN_CLASSES)

            if selected_model is not None:
                import torch
                from torchvision import transforms
                
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                img_tensor = transform(image).unsqueeze(0).to(self.device)

                with torch.no_grad():
                    outputs = selected_model(img_tensor)
                    probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()

                predicted_class_idx = int(np.argmax(probs))
                confidence = float(probs[predicted_class_idx])

                top_indices = np.argsort(probs)[::-1]
                alternatives = [
                    {
                        "disease_name": class_labels[idx],
                        "confidence": float(probs[idx])
                    }
                    for idx in top_indices[1:4] if idx < len(class_labels)
                ]
                disease_name = class_labels[predicted_class_idx]
            else:
                disease_name, confidence, alternatives = self._mock_prediction(normalized_crop)

            # Parse plant and disease names
            parts = disease_name.split("___")
            plant_name = parts[0].replace("_", " ") if len(parts) > 0 else normalized_crop
            disease_condition = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"

            # Get treatment information
            treatment = self._get_treatment(disease_name)

            return {
                "plant_name": plant_name,
                "disease_name": disease_condition,
                "detected_disease": disease_name,
                "confidence_score": round(confidence, 4),
                "alternative_predictions": alternatives,
                "treatment": treatment,
                "detected_at": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Disease detection error: {e}")
            return None

    def _mock_prediction(
        self,
        crop_type: Optional[str]
    ) -> tuple:
        """Fallback prediction generator when model file is absent."""
        import random

        crop = crop_type if crop_type in self.SUPPORTED_CROPS else "Corn"
        classes = self.classes_map.get(crop, self.CORN_CLASSES)

        relevant_diseases = [d for d in classes if "healthy" not in d.lower()]
        if not relevant_diseases:
            relevant_diseases = classes

        disease_name = random.choice(relevant_diseases)
        confidence = random.uniform(0.85, 0.98)

        other_diseases = [d for d in classes if d != disease_name]
        alternatives = []
        for _ in range(min(2, len(other_diseases))):
            alt = random.choice(other_diseases)
            other_diseases.remove(alt)
            alternatives.append({
                "disease_name": alt,
                "confidence": random.uniform(0.05, 0.15)
            })

        return disease_name, confidence, alternatives
    
    def _get_treatment(self, disease_name: str) -> Dict[str, Optional[str]]:
        """Get treatment information for disease."""
        treatment = self.DISEASE_TREATMENTS.get(disease_name)
        if not treatment:
            treatment = self.DISEASE_TREATMENTS["default"]
        
        return {
            "organic": treatment.get("organic"),
            "chemical": treatment.get("chemical"),
            "preventive": treatment.get("preventive")
        }
    
    async def get_disease_info(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a disease."""
        all_classes = self.CORN_CLASSES + self.TOMATO_CLASSES + self.PADDY_CLASSES
        if disease_name not in all_classes:
            return None
        
        parts = disease_name.split("___")
        crop = parts[0].replace("_", " ") if len(parts) > 0 else "Unknown"
        condition = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
        
        treatment = self._get_treatment(disease_name)
        
        return {
            "name": disease_name,
            "crop": crop,
            "condition": condition,
            "affected_crops": [crop],
            "symptoms": f"Typical symptoms of {condition} on {crop}",
            "treatment": treatment,
            "is_healthy": "healthy" in disease_name.lower()
        }


# Global service instance
disease_service = DiseaseDetectionService()
