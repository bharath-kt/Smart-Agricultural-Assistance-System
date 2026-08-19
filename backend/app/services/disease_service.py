"""Plant disease detection service supporting Tomato, Corn, and Paddy models."""

import io
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
from PIL import Image

from app.core.logging import get_logger

logger = get_logger(__name__)


class DiseaseDetectionService:
    """Disease detection using PyTorch MobileNetV2 models."""

    SUPPORTED_CROPS = ["Tomato", "Corn", "Paddy"]

    CORN_CLASSES = [
        "Corn_(maize)___Blight",
        "Corn_(maize)___Common_Rust",
        "Corn_(maize)___Gray_Leaf_Spot",
        "Corn_(maize)___Healthy",
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
        "Tomato___powdery_mildew",
    ]

    PADDY_CLASSES = [
        "Paddy___Bacterial_leaf_blight",
        "Paddy___Brown_spot",
        "Paddy___Leaf_smut",
        "Paddy___healthy",
    ]

    DISEASE_TREATMENTS = {
        "Corn_(maize)___Blight": {
            "organic": "Remove infected debris, rotate crops, apply copper spray or neem oil",
            "chemical": "Apply fungicides with mancozeb, chlorothalonil, or azoxystrobin",
            "preventive": "Plant resistant hybrids, practice 3-year crop rotation, avoid continuous corn planting",
        },

        "Corn_(maize)___Common_Rust": {
            "organic": "Plant resistant varieties, remove infected leaves, improve field sanitation",
            "chemical": "Apply fungicides with azoxystrobin or propiconazole if severe",
            "preventive": "Use resistant hybrids, early planting, practice crop rotation",
        },

        "Corn_(maize)___Gray_Leaf_Spot": {
            "organic": "Remove infected crop debris, improve field sanitation, apply neem oil",
            "chemical": "Apply fungicides with azoxystrobin or pyraclostrobin",
            "preventive": "Crop rotation, use resistant hybrids, maintain balanced soil fertilization",
        },

        "Corn_(maize)___Healthy": {
            "organic": "Maintain regular care, adequate watering, and organic soil composting",
            "chemical": "No chemical treatment required; plant is healthy",
            "preventive": "Continue crop rotation, regular field monitoring, and proper plant spacing",
        },

        "Tomato___Bacterial_spot": {
            "organic": "Remove infected leaves, apply copper-based bactericides, avoid working when wet",
            "chemical": "Apply copper hydroxide or streptomycin sulfate",
            "preventive": "Use disease-free seeds, sanitize tools, avoid overhead irrigation",
        },

        "Tomato___Early_blight": {
            "organic": "Remove lower infected leaves, mulch around plants, apply copper spray",
            "chemical": "Apply chlorothalonil or mancozeb fungicides",
            "preventive": "Rotate crops, stake plants, avoid wetting foliage",
        },

        "Tomato___Late_blight": {
            "organic": "Remove infected plants immediately, apply copper fungicide",
            "chemical": "Apply metalaxyl-m or cymoxanil fungicides urgently",
            "preventive": "Use resistant varieties, ensure good drainage, avoid overhead watering",
        },

        "Tomato___Leaf_Mold": {
            "organic": "Improve ventilation, remove infected leaves, apply neem oil",
            "chemical": "Apply fungicides with chlorothalonil or mancozeb",
            "preventive": "Ensure proper spacing, avoid high humidity, plant resistant varieties",
        },

        "Tomato___Septoria_leaf_spot": {
            "organic": "Remove infected lower leaves, mulch around plants, apply copper spray",
            "chemical": "Apply fungicides with chlorothalonil or mancozeb",
            "preventive": "Rotate crops, stake plants, remove crop debris",
        },

        "Tomato___Spider_mites Two-spotted_spider_mite": {
            "organic": "Spray water on undersides of leaves, introduce predatory mites, apply neem oil",
            "chemical": "Apply miticides with abamectin or spiromesifen",
            "preventive": "Maintain humidity, monitor regularly, avoid dusty conditions",
        },

        "Tomato___Target_Spot": {
            "organic": "Remove infected leaves, improve air circulation, apply copper fungicide",
            "chemical": "Apply fungicides with boscalid or chlorothalonil",
            "preventive": "Proper spacing, avoid overhead irrigation, plant resistant varieties",
        },

        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
            "organic": "Remove infected plants, control whiteflies with sticky traps and neem oil",
            "chemical": "Apply insecticides for whitefly control",
            "preventive": "Use resistant varieties, netting to block whiteflies, reflective mulches",
        },

        "Tomato___Tomato_mosaic_virus": {
            "organic": "Remove infected plants, sanitize tools, control aphids",
            "chemical": "No chemical cure; focus on aphid and vector control",
            "preventive": "Use resistant varieties, sanitize hands/tools, avoid tobacco use near plants",
        },

        "Tomato___healthy": {
            "organic": "Maintain regular care, proper staking, and organic soil composting",
            "chemical": "No chemical treatment required; plant is healthy",
            "preventive": "Continue crop rotation, regular field monitoring, and proper plant spacing",
        },

        "Tomato___powdery_mildew": {
            "organic": "Spray with sulfur or potassium bicarbonate, apply neem oil, improve air circulation",
            "chemical": "Apply sulfur-based fungicides or myclobutanil",
            "preventive": "Provide adequate spacing, plant in full sun, avoid high nitrogen fertilizers",
        },

        "Paddy___Bacterial_leaf_blight": {
            "organic": "Ensure field drainage, apply balanced fertilizers, avoid excessive nitrogen",
            "chemical": "Apply copper hydroxide + streptomycin sulfate",
            "preventive": "Use resistant rice varieties, avoid deep water during tillering",
        },

        "Paddy___Brown_spot": {
            "organic": "Improve soil fertility, apply potassium and micronutrients",
            "chemical": "Apply mancozeb or edifenphos",
            "preventive": "Use seed treatment, ensure balanced soil nutrition",
        },

        "Paddy___Leaf_smut": {
            "organic": "Remove infected plants, maintain clean field borders",
            "chemical": "Apply copper-based fungicides if severe",
            "preventive": "Practice crop rotation, balanced fertilization",
        },

        "Paddy___healthy": {
            "organic": "Maintain proper water level and organic soil fertility",
            "chemical": "No chemical treatment required; crop is healthy",
            "preventive": "Regular field inspection, proper weed management",
        },

        "default": {
            "organic": "Remove infected plant parts and improve field sanitation",
            "chemical": "Consult local agricultural extension for appropriate treatment",
            "preventive": "Practice crop rotation, maintain plant health, and ensure proper spacing",
        },
    }

    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.classes_map: Dict[str, list] = {}
        self.device = None

        self._load_models()

    # =========================================================
    # MODEL LOADING
    # =========================================================

    def _load_models(self):
        """Load available PyTorch models."""

        try:
            import torch
            import torch.nn as nn
            from torchvision import models

            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )

            logger.info(
                f"Loading disease models using device: {self.device}"
            )

            backend_root = Path(__file__).resolve().parents[2]

            # =================================================
            # CORN MODEL
            # =================================================

            corn_paths = [
                backend_root / "ml_models" / "plant_disease_model.pth",
                backend_root
                / "ml_models"
                / "plant"
                / "corn"
                / "corn_disease_model.pth",
            ]

            corn_path = next(
                (path for path in corn_paths if path.exists()),
                None,
            )

            if corn_path:

                logger.info(
                    f"Loading Corn model from: {corn_path}"
                )

                checkpoint = torch.load(
                    str(corn_path),
                    map_location=self.device,
                )

                classes = checkpoint.get(
                    "classes",
                    [
                        "Blight",
                        "Common_Rust",
                        "Gray_Leaf_Spot",
                        "Healthy",
                    ],
                )

                logger.info(
                    f"Corn checkpoint classes: {classes}"
                )

                model_corn = models.mobilenet_v2()

                in_features = model_corn.classifier[1].in_features

                model_corn.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_features, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, len(classes)),
                )

                model_corn.load_state_dict(
                    checkpoint["model_state_dict"]
                )

                model_corn.to(self.device)
                model_corn.eval()

                self.models["Corn"] = model_corn

                self.classes_map["Corn"] = self._normalize_classes(
                    classes,
                    "Corn",
                )

                logger.info(
                    f"Corn model loaded successfully: {corn_path}"
                )

                logger.info(
                    f"Corn normalized classes: "
                    f"{self.classes_map['Corn']}"
                )

            else:
                logger.warning(
                    "Corn disease model not found."
                )

            # =================================================
            # TOMATO MODEL
            # =================================================

            tomato_paths = [
                backend_root
                / "ml_models"
                / "plant"
                / "tomato"
                / "tomato_disease_model.pth",
            ]

            tomato_path = next(
                (path for path in tomato_paths if path.exists()),
                None,
            )

            if tomato_path:

                logger.info(
                    f"Loading Tomato model from: {tomato_path}"
                )

                checkpoint = torch.load(
                    str(tomato_path),
                    map_location=self.device,
                )

                classes = checkpoint.get(
                    "classes",
                    [
                        c.replace("Tomato___", "")
                        for c in self.TOMATO_CLASSES
                    ],
                )

                logger.info(
                    f"Tomato checkpoint classes: {classes}"
                )

                model_tomato = models.mobilenet_v2()

                in_features = model_tomato.classifier[1].in_features

                model_tomato.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_features, 256),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(256, len(classes)),
                )

                model_tomato.load_state_dict(
                    checkpoint["model_state_dict"]
                )

                model_tomato.to(self.device)
                model_tomato.eval()

                self.models["Tomato"] = model_tomato

                self.classes_map["Tomato"] = self._normalize_classes(
                    classes,
                    "Tomato",
                )

                logger.info(
                    f"Tomato model loaded successfully: {tomato_path}"
                )

                logger.info(
                    f"Tomato normalized classes: "
                    f"{self.classes_map['Tomato']}"
                )

            else:
                logger.warning(
                    "Tomato disease model not found."
                )

            # =================================================
            # PADDY MODEL
            # =================================================

            paddy_paths = [
                backend_root
                / "ml_models"
                / "plant"
                / "paddy"
                / "paddy_disease_model.pth",
            ]

            paddy_path = next(
                (path for path in paddy_paths if path.exists()),
                None,
            )

            if paddy_path:

                logger.info(
                    f"Loading Paddy model from: {paddy_path}"
                )

                checkpoint = torch.load(
                    str(paddy_path),
                    map_location=self.device,
                )

                classes = checkpoint.get(
                    "classes",
                    [
                        c.replace("Paddy___", "")
                        for c in self.PADDY_CLASSES
                    ],
                )

                logger.info(
                    f"Paddy checkpoint classes: {classes}"
                )

                model_paddy = models.mobilenet_v2()

                in_features = model_paddy.classifier[1].in_features

                model_paddy.classifier = nn.Sequential(
                    nn.Dropout(0.3),
                    nn.Linear(in_features, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, len(classes)),
                )

                model_paddy.load_state_dict(
                    checkpoint["model_state_dict"]
                )

                model_paddy.to(self.device)
                model_paddy.eval()

                self.models["Paddy"] = model_paddy

                self.classes_map["Paddy"] = self._normalize_classes(
                    classes,
                    "Paddy",
                )

                logger.info(
                    f"Paddy model loaded successfully: {paddy_path}"
                )

                logger.info(
                    f"Paddy normalized classes: "
                    f"{self.classes_map['Paddy']}"
                )

            else:
                logger.warning(
                    "Paddy disease model not found."
                )

            # =================================================
            # MODEL STATUS DEBUG
            # =================================================

            logger.info(
                "========== DISEASE MODEL STATUS =========="
            )

            for crop in self.SUPPORTED_CROPS:
                logger.info(
                    f"{crop}: "
                    f"model_loaded={crop in self.models}, "
                    f"classes={self.classes_map.get(crop, [])}"
                )

            logger.info(
                f"Available model keys: {list(self.models.keys())}"
            )

            logger.info(
                "=========================================="
            )

        except Exception as error:

            logger.exception(
                f"Error loading disease models: {error}"
            )

    # =========================================================
    # CLASS NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_classes(classes, crop: str):
        """Normalize checkpoint class names without duplicating prefixes."""

        normalized = []

        for class_name in classes:

            class_name = str(class_name)

            if crop == "Corn":

                if class_name.startswith(
                    "Corn_(maize)___"
                ):
                    normalized.append(
                        class_name
                    )

                elif class_name.startswith(
                    "Corn___"
                ):
                    normalized.append(
                        class_name.replace(
                            "Corn___",
                            "Corn_(maize)___",
                            1,
                        )
                    )

                else:
                    normalized.append(
                        f"Corn_(maize)___{class_name}"
                    )

            elif crop == "Tomato":

                if class_name.startswith(
                    "Tomato___"
                ):
                    normalized.append(
                        class_name
                    )

                else:
                    normalized.append(
                        f"Tomato___{class_name}"
                    )

            elif crop == "Paddy":

                if class_name.startswith(
                    "Paddy___"
                ):
                    normalized.append(
                        class_name
                    )

                else:
                    normalized.append(
                        f"Paddy___{class_name}"
                    )

        return normalized

    # =========================================================
    # RELOAD
    # =========================================================

    def reload_models(self):
        """Reload disease models from disk."""

        logger.info(
            "========== RELOADING DISEASE MODELS =========="
        )

        self.models = {}
        self.classes_map = {}

        self._load_models()

    # =========================================================
    # DISEASE DETECTION
    # =========================================================

    async def detect_disease(
        self,
        image_bytes: bytes,
        crop_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        try:

            # =================================================
            # DEBUG: RAW CROP RECEIVED FROM FRONTEND
            # =================================================

            logger.info(
                "========== DISEASE DETECTION REQUEST =========="
            )

            logger.info(
                f"Raw crop_type received from frontend: "
                f"{crop_type!r}"
            )

            logger.info(
                f"Image size received: {len(image_bytes)} bytes"
            )

            # =================================================
            # CROP VALIDATION
            # =================================================

            if not crop_type or not crop_type.strip():

                logger.error(
                    "Crop type was NOT provided by frontend."
                )

                return {
                    "error": (
                        "Crop type is required. "
                        "Please select Tomato, Corn, or Paddy "
                        "before uploading the image."
                    ),
                    "supported_crops": self.SUPPORTED_CROPS,
                }

            crop_value = crop_type.strip().lower()

            crop_mapping = {
                "tomato": "Tomato",
                "corn": "Corn",
                "maize": "Corn",
                "paddy": "Paddy",
                "rice": "Paddy",
            }

            normalized_crop = crop_mapping.get(
                crop_value
            )

            logger.info(
                f"Normalized crop selected: "
                f"{normalized_crop}"
            )

            if normalized_crop is None:

                logger.error(
                    f"Unsupported crop received: "
                    f"{crop_type!r}"
                )

                return {
                    "error": (
                        f"Unsupported plant '{crop_type}'. "
                        "Please select Tomato, Corn, or Paddy."
                    ),
                    "supported_crops": self.SUPPORTED_CROPS,
                }

            logger.info(
                f"FINAL MODEL SELECTION: "
                f"{normalized_crop}"
            )

            # =================================================
            # MAKE SURE MODEL EXISTS
            # =================================================

            if normalized_crop not in self.models:

                logger.warning(
                    f"{normalized_crop} model is not loaded. "
                    "Reloading models..."
                )

                self.reload_models()

            selected_model = self.models.get(
                normalized_crop
            )

            if selected_model is None:

                logger.error(
                    f"No trained model available for "
                    f"{normalized_crop}"
                )

                return {
                    "error": (
                        f"The {normalized_crop} disease detection "
                        "model is not available on the server."
                    ),
                    "crop": normalized_crop,
                }

            class_labels = self.classes_map.get(
                normalized_crop,
                [],
            )

            logger.info(
                f"Using {normalized_crop} model"
            )

            logger.info(
                f"Class labels: {class_labels}"
            )

            if not class_labels:

                logger.error(
                    f"No class labels available for "
                    f"{normalized_crop} model."
                )

                return {
                    "error": (
                        f"No class labels available for "
                        f"{normalized_crop} model."
                    )
                }

            # =================================================
            # IMAGE PROCESSING
            # =================================================

            image = Image.open(
                io.BytesIO(image_bytes)
            ).convert("RGB")

            logger.info(
                f"Image successfully opened: "
                f"{image.size}"
            )

            from torchvision import transforms

            transform = transforms.Compose(
                [
                    transforms.Resize(
                        (224, 224)
                    ),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[
                            0.485,
                            0.456,
                            0.406,
                        ],
                        std=[
                            0.229,
                            0.224,
                            0.225,
                        ],
                    ),
                ]
            )

            image_tensor = (
                transform(image)
                .unsqueeze(0)
                .to(self.device)
            )

            # =================================================
            # PREDICTION
            # =================================================

            import torch

            with torch.no_grad():

                outputs = selected_model(
                    image_tensor
                )

                probabilities = torch.softmax(
                    outputs,
                    dim=1,
                )[0].cpu().numpy()

            predicted_index = int(
                np.argmax(probabilities)
            )

            logger.info(
                f"Prediction index: "
                f"{predicted_index}"
            )

            # =================================================
            # SAFETY CHECK
            # =================================================

            if predicted_index >= len(
                class_labels
            ):

                logger.error(
                    "Model output index does not "
                    "match class list."
                )

                return {
                    "error": (
                        "Model class configuration mismatch."
                    )
                }

            confidence = float(
                probabilities[predicted_index]
            )

            disease_name = class_labels[
                predicted_index
            ]

            logger.info(
                f"Predicted class: {disease_name}"
            )

            logger.info(
                f"Prediction confidence: "
                f"{confidence:.2%}"
            )

            # =================================================
            # ALTERNATIVE PREDICTIONS
            # =================================================

            sorted_indices = np.argsort(
                probabilities
            )[::-1]

            alternatives = []

            for index in sorted_indices[1:4]:

                index = int(index)

                if index < len(
                    class_labels
                ):

                    alternatives.append(
                        {
                            "disease_name":
                                class_labels[index],

                            "confidence":
                                round(
                                    float(
                                        probabilities[index]
                                    ),
                                    4,
                                ),
                        }
                    )

            # =================================================
            # PARSE RESULT
            # =================================================

            parts = disease_name.split(
                "___"
            )

            if len(parts) >= 2:

                plant_name = parts[0].replace(
                    "_",
                    " ",
                )

                disease_condition = parts[1].replace(
                    "_",
                    " ",
                )

            else:

                plant_name = normalized_crop

                disease_condition = (
                    disease_name
                )

            # =================================================
            # CORN DISPLAY NAME
            # =================================================

            if plant_name.lower() in [
                "corn (maize)",
                "corn",
            ]:

                plant_name = "Corn (maize)"

            # =================================================
            # TREATMENT
            # =================================================

            treatment = self._get_treatment(
                disease_name
            )

            # =================================================
            # FINAL RESPONSE
            # =================================================

            result = {
                "plant_name": plant_name,

                "disease_name":
                    disease_condition,

                "detected_disease":
                    disease_name,

                "confidence_score":
                    round(
                        confidence,
                        4,
                    ),

                "alternative_predictions":
                    alternatives,

                "treatment":
                    treatment,

                "crop_type":
                    normalized_crop,

                "detected_at":
                    datetime.utcnow(),
            }

            logger.info(
                "========== FINAL DISEASE RESULT =========="
            )

            logger.info(
                f"Requested crop: {normalized_crop}"
            )

            logger.info(
                f"Plant: {plant_name}"
            )

            logger.info(
                f"Disease: {disease_condition}"
            )

            logger.info(
                f"Confidence: {confidence:.2%}"
            )

            logger.info(
                "==========================================="
            )

            return result

        except Exception as error:

            logger.exception(
                f"Disease detection error: {error}"
            )

            return {
                "error": "Disease detection failed.",
                "details": str(error),
            }

    # =========================================================
    # TREATMENT
    # =========================================================

    def _get_treatment(
        self,
        disease_name: str,
    ) -> Dict[str, Optional[str]]:

        treatment = self.DISEASE_TREATMENTS.get(
            disease_name
        )

        if not treatment:

            treatment = self.DISEASE_TREATMENTS[
                "default"
            ]

        return {
            "organic": treatment.get(
                "organic"
            ),

            "chemical": treatment.get(
                "chemical"
            ),

            "preventive": treatment.get(
                "preventive"
            ),
        }

    # =========================================================
    # DISEASE INFORMATION
    # =========================================================

    async def get_disease_info(
        self,
        disease_name: str,
    ) -> Optional[Dict[str, Any]]:

        all_classes = (
            self.CORN_CLASSES
            + self.TOMATO_CLASSES
            + self.PADDY_CLASSES
        )

        if disease_name not in all_classes:
            return None

        parts = disease_name.split(
            "___"
        )

        crop = (
            parts[0].replace(
                "_",
                " ",
            )
            if len(parts) > 0
            else "Unknown"
        )

        condition = (
            parts[1].replace(
                "_",
                " ",
            )
            if len(parts) > 1
            else "Unknown"
        )

        treatment = self._get_treatment(
            disease_name
        )

        return {
            "name": disease_name,

            "crop": crop,

            "condition": condition,

            "affected_crops": [crop],

            "symptoms": (
                f"Typical symptoms of "
                f"{condition} on {crop}"
            ),

            "treatment": treatment,

            "is_healthy": (
                "healthy"
                in disease_name.lower()
            ),
        }


# =============================================================
# GLOBAL SERVICE INSTANCE
# =============================================================

disease_service = DiseaseDetectionService()