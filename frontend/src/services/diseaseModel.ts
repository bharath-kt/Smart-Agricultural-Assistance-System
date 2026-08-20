import type { DiseasePrediction } from '../types';

// Supported crops
export const SUPPORTED_CROPS = ['Tomato', 'Corn'];

// Crop localization
export const CROP_LOCALIZATION: Record<string, { en: string; kn: string }> = {
  Tomato: { en: 'Tomato', kn: 'ಟೊಮೆಟೊ (Tomato)' },
  Corn: { en: 'Corn', kn: 'ಮೆಕ್ಕೆಜೋಳ (Corn)' }
};

// Plant disease classes
export const DISEASE_CLASSES = [
  'Corn Blight',
  'Corn Common Rust',
  'Corn Gray Leaf Spot',
  'Corn Healthy',
  'Tomato Bacterial Spot',
  'Tomato Early Blight',
  'Tomato Late Blight',
  'Tomato Leaf Mold',
  'Tomato Septoria Leaf Spot',
  'Tomato Spider Mites',
  'Tomato Target Spot',
  'Tomato Yellow Leaf Curl Virus',
  'Tomato Mosaic Virus',
  'Tomato Healthy'
];

// Kannada disease translations
export const DISEASE_KN_TRANSLATIONS: Record<
  string,
  {
    plantName: string;
    diseaseName: string;
    disease: string;
    description: string;
    treatment: string[];
    prevention: string[];
  }
> = {
  'Tomato Early Blight': {
    plantName: 'ಟೊಮೆಟೊ',
    diseaseName: 'ಅರ್ಲಿ ಬ್ಲೈಟ್ (Early Blight)',
    disease: 'ಟೊಮೆಟೊ ಅರ್ಲಿ ಬ್ಲೈಟ್',
    description:
      'ಟೊಮೆಟೊ ಎಲೆಗಳ ಮೇಲೆ ಕಪ್ಪು ಚುಕ್ಕೆಗಳು ಮತ್ತು ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುವುದು ಕಂಡುಬಂದಿದೆ. ಇದು ಶಿಲೀಂಧ್ರ ರೋಗವಾಗಿದೆ.',
    treatment: [
      'ಸೋಂಕಿತ ಸಸ್ಯದ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ ನಾಶಪಡಿಸಿ',
      'ಪ್ರತಿ 7-10 ದಿನಗಳಿಗೊಮ್ಮೆ ತಾಮ್ರ ಆಧಾರಿತ ಶಿಲೀಂಧ್ರನಾಶಕವನ್ನು ಸಿಂಪಡಿಸಿ',
      'ಉತ್ತಮ ಗಾಳಿ ಸಂಚಾರಕ್ಕಾಗಿ ಸಸ್ಯಗಳ ನಡುವೆ ಸರಿಯಾದ ಅಂತರ ಕಾಯ್ದುಕೊಳ್ಳಿ',
      'ಬುಡಕ್ಕೆ ಮಾತ್ರ ನೀರು ಹಾಕಿ, ಎಲೆಗಳನ್ನು ನೆನೆಸಬೇಡಿ'
    ],
    prevention: [
      'ಪ್ರತಿ 3 ವರ್ಷಕ್ಕೊಮ್ಮೆ ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ',
      'ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬಳಸಿ',
      'ಮಣ್ಣಿನ ತೇವಾಂಶ ಸಂರಕ್ಷಣೆಗೆ ಹೊದಿಕೆ (Mulch) ಬಳಸಿ'
    ]
  },

  'Corn Blight': {
    plantName: 'ಮೆಕ್ಕೆಜೋಳ',
    diseaseName: 'ಬ್ಲೈಟ್ ರೋಗ (Blight)',
    disease: 'ಮೆಕ್ಕೆಜೋಳ ಬ್ಲೈಟ್',
    description:
      'ಮೆಕ್ಕೆಜೋಳ ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಬಣ್ಣದ ಕಲೆಗಳು ಮತ್ತು ಒಣಗುವಿಕೆ ಕಂಡುಬಂದಿದೆ.',
    treatment: [
      'ಸೋಂಕಿತ ಸಸ್ಯದ ಭಾಗಗಳನ್ನು ತೆಗೆದುಹಾಕಿ',
      'ಮ್ಯಾಂಕೋಜೆಬ್ ಅಥವಾ ಕ್ಲೋರೋಥಲೋನಿಲ್ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ',
      'ಸರಿಯಾದ ಗಾಳಿಯ ಸಂಚಾರವನ್ನು ಕಾಯ್ದುಕೊಳ್ಳಿ'
    ],
    prevention: [
      'ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ',
      '3 ವರ್ಷಕ್ಕೊಮ್ಮೆ ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ',
      'ಸರಿಯಾದ ಅಂತರದಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ'
    ]
  },

  'Corn Common Rust': {
    plantName: 'ಮೆಕ್ಕೆಜೋಳ',
    diseaseName: 'ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ (Common Rust)',
    disease: 'ಮೆಕ್ಕೆಜೋಳ ತುಕ್ಕು ರೋಗ',
    description:
      'ಎಲೆಗಳ ಮೇಲೆ ಕಂದು ಅಥವಾ ಕೆಂಪು ಬಣ್ಣದ ಗುಳ್ಳೆಗಳು ಕಂಡುಬರುತ್ತವೆ.',
    treatment: [
      'ತೀವ್ರವಾಗಿದ್ದರೆ ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಶಿಲೀಂಧ್ರನಾಶಕ ಸಿಂಪಡಿಸಿ',
      'ಹೆಚ್ಚು ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದುಹಾಕಿ'
    ],
    prevention: [
      'ರೋಗ ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ',
      'ಬೇಗನೆ ಬಿತ್ತನೆ ಮಾಡಿ',
      'ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ'
    ]
  },

  'Corn Gray Leaf Spot': {
    plantName: 'ಮೆಕ್ಕೆಜೋಳ',
    diseaseName: 'ಗ್ರೇ ಲೀಫ್ ಸ್ಪಾಟ್ (Gray Leaf Spot)',
    disease: 'ಮೆಕ್ಕೆಜೋಳ ಗ್ರೇ ಲೀಫ್ ಸ್ಪಾಟ್',
    description:
      'ಎಲೆಗಳ ನರಗಳ ನಡುವೆ ಆಯತಾಕಾರದ ಬೂದು-ಕಂದು ಬಣ್ಣದ ಕಲೆಗಳು ಕಂಡುಬರುತ್ತವೆ.',
    treatment: [
      'ಅಜೋಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ ಅಥವಾ ಪೈರಾಕ್ಲೋಸ್ಟ್ರೋಬಿನ್ ಸಿಂಪಡಿಸಿ',
      'ಸೋಂಕಿತ ತ್ಯಾಜ್ಯವನ್ನು ತೆಗೆದುಹಾಕಿ'
    ],
    prevention: [
      'ಬೆಳೆ ಪರಿವರ್ತನೆ ಮಾಡಿ',
      'ರೋಗ ನಿರೋಧಕ ಹೈಬ್ರಿಡ್‌ಗಳನ್ನು ಬಳಸಿ',
      'ಸಮತೋಲಿತ ರಸಗೊಬ್ಬರ ನೀಡಿ'
    ]
  },

  'Corn Healthy': {
    plantName: 'ಮೆಕ್ಕೆಜೋಳ',
    diseaseName: 'ಆರೋಗ್ಯಕರ ಸಸ್ಯ',
    disease: 'ಆರೋಗ್ಯಕರ ಸಸ್ಯ',
    description:
      'ಸಸ್ಯವು ಸಂಪೂರ್ಣವಾಗಿ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಮತ್ತು ರೋಗದ ಯಾವುದೇ ಚಿಹ್ನೆಗಳಿಲ್ಲ.',
    treatment: ['ನಿಯಮಿತ ಆರೈಕೆ ಮತ್ತು ನೀರಾವರಿ ಮುಂದುವರಿಸಿ'],
    prevention: ['ಸಾಮಾನ್ಯ ಬೆಳೆ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ']
  },

  'Tomato Healthy': {
    plantName: 'ಟೊಮೆಟೊ',
    diseaseName: 'ಆರೋಗ್ಯಕರ ಸಸ್ಯ',
    disease: 'ಆರೋಗ್ಯಕರ ಟೊಮೆಟೊ ಸಸ್ಯ',
    description:
      'ಟೊಮೆಟೊ ಸಸ್ಯವು ಆರೋಗ್ಯಕರವಾಗಿದೆ ಮತ್ತು ರೋಗದ ಯಾವುದೇ ಸ್ಪಷ್ಟ ಚಿಹ್ನೆಗಳಿಲ್ಲ.',
    treatment: ['ನಿಯಮಿತ ಆರೈಕೆ ಮತ್ತು ನೀರಾವರಿ ಮುಂದುವರಿಸಿ'],
    prevention: ['ಸಾಮಾನ್ಯ ಬೆಳೆ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ']
  },

  'Healthy': {
    plantName: 'ಸಸ್ಯ',
    diseaseName: 'ಆರೋಗ್ಯಕರ ಸಸ್ಯ',
    disease: 'ಆರೋಗ್ಯಕರ ಸಸ್ಯ',
    description:
      'ಸಸ್ಯವು ಸಂಪೂರ್ಣವಾಗಿ ಆರೋಗ್ಯಕರವಾಗಿದೆ ಮತ್ತು ರೋಗದ ಯಾವುದೇ ಚಿಹ್ನೆಗಳಿಲ್ಲ.',
    treatment: ['ನಿಯಮಿತ ಆರೈಕೆ ಮತ್ತು ನೀರಾವರಿ ಮುಂದುವರಿಸಿ'],
    prevention: ['ಸಾಮಾನ್ಯ ಬೆಳೆ ನಿರ್ವಹಣೆ ಮುಂದುವರಿಸಿ']
  }
};

// Load disease model
export async function loadDiseaseModel(): Promise<boolean> {
  try {
    console.log('Disease detection service ready');
    return true;
  } catch (error) {
    console.error('Failed to load disease model:', error);
    return false;
  }
}

// Translate prediction to Kannada
export function translatePrediction(
  pred: DiseasePrediction,
  lang: string
): DiseasePrediction {
  if (lang === 'kn') {
    const key = pred.diseaseName || pred.disease;

    const kn =
      DISEASE_KN_TRANSLATIONS[key] ||
      (pred.disease.includes('Healthy')
        ? DISEASE_KN_TRANSLATIONS['Healthy']
        : null);

    if (kn) {
      return {
        ...pred,
        plantName: kn.plantName,
        diseaseName: kn.diseaseName,
        disease: kn.disease,
        description: kn.description,
        treatment: kn.treatment,
        prevention: kn.prevention
      };
    }
  }

  return pred;
}

// Predict disease
export async function predictDisease(
  imageFile: File,
  cropType?: string,
  token?: string
): Promise<DiseasePrediction> {
  if (!cropType || !cropType.trim()) {
    throw new Error('Please select a crop.');
  }

  if (!SUPPORTED_CROPS.includes(cropType)) {
    throw new Error('Unsupported crop. Only Tomato and Corn are supported.');
  }

  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('crop_type', cropType);

  const headers: Record<string, string> = {};

  const authToken = token || localStorage.getItem('smart_agri_token');
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const endpoint = `${apiUrl}/disease/detect`;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: formData
    });

    if (!response.ok) {
      let errorMsg = 'Unable to analyze the image. Please try again.';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        } else if (errorData.error) {
          errorMsg = errorData.error;
        }
      } catch {
        // ignore JSON parse error
      }
      throw new Error(errorMsg);
    }

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    const plantName = data.plant_name || cropType;
    const diseaseName = data.disease_name || 'Healthy';
    const isHealthy = diseaseName.toLowerCase().includes('healthy');

    const treatmentList: string[] = [];
    if (data.treatment?.organic) {
      treatmentList.push(`Organic: ${data.treatment.organic}`);
    }
    if (data.treatment?.chemical) {
      treatmentList.push(`Chemical: ${data.treatment.chemical}`);
    }
    if (treatmentList.length === 0) {
      treatmentList.push(
        isHealthy
          ? 'Continue regular care and monitoring'
          : 'Apply appropriate fungicide and practice sanitation'
      );
    }

    const preventionList: string[] = [];
    if (data.treatment?.preventive) {
      preventionList.push(data.treatment.preventive);
    } else {
      preventionList.push(
        'Practice crop rotation, maintain field sanitation, and monitor regularly'
      );
    }

    return {
      plantName,
      diseaseName,
      disease: isHealthy
        ? 'Healthy Plant'
        : `${plantName} ${diseaseName}`,
      confidence: Math.round((data.confidence_score || 0.95) * 100),
      description: isHealthy
        ? 'The plant appears to be healthy with no signs of disease.'
        : `Detected ${diseaseName} on ${plantName}. This is a common plant disease that requires attention.`,
      treatment: treatmentList,
      prevention: preventionList
    };
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw err;
    }
    throw new Error('Unable to analyze the image. Please try again.');
  }
}

// Get supported crops
export function getSupportedCrops(): string[] {
  return SUPPORTED_CROPS;
}