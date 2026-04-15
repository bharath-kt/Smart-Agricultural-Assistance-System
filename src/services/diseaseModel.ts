import * as tf from '@tensorflow/tfjs';
import type { DiseasePrediction } from '../types';

// Plant disease classes (simplified for demo - in production, use full model)
const DISEASE_CLASSES = [
  'Apple Scab',
  'Apple Black Rot',
  'Apple Cedar Rust',
  'Apple Healthy',
  'Blueberry Healthy',
  'Cherry Powdery Mildew',
  'Cherry Healthy',
  'Corn Cercospora Leaf Spot',
  'Corn Common Rust',
  'Corn Northern Leaf Blight',
  'Corn Healthy',
  'Grape Black Rot',
  'Grape Esca (Black Measles)',
  'Grape Leaf Blight',
  'Grape Healthy',
  'Orange Haunglongbing (Citrus Greening)',
  'Peach Bacterial Spot',
  'Peach Healthy',
  'Pepper Bell Bacterial Spot',
  'Pepper Bell Healthy',
  'Potato Early Blight',
  'Potato Late Blight',
  'Potato Healthy',
  'Raspberry Healthy',
  'Soybean Healthy',
  'Squash Powdery Mildew',
  'Strawberry Leaf Scorch',
  'Strawberry Healthy',
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

// Treatment recommendations for common diseases
const TREATMENTS: { [key: string]: { treatment: string[]; prevention: string[] } } = {
  'Tomato Early Blight': {
    treatment: [
      'Remove and destroy infected plant parts',
      'Apply copper-based fungicide every 7-10 days',
      'Ensure proper spacing for air circulation',
      'Water at the base, avoid wetting leaves'
    ],
    prevention: [
      'Rotate crops every 3 years',
      'Use disease-resistant varieties',
      'Mulch to prevent soil splash',
      'Maintain proper plant nutrition'
    ]
  },
  'Tomato Late Blight': {
    treatment: [
      'Remove infected plants immediately',
      'Apply fungicide with chlorothalonil or mancozeb',
      'Increase air circulation around plants',
      'Avoid overhead irrigation'
    ],
    prevention: [
      'Plant resistant varieties',
      'Space plants properly',
      'Monitor weather conditions',
      'Apply preventive fungicides'
    ]
  },
  'Potato Early Blight': {
    treatment: [
      'Apply protective fungicides',
      'Remove infected leaves',
      'Ensure adequate irrigation',
      'Use balanced fertilization'
    ],
    prevention: [
      'Practice crop rotation',
      'Use certified seed potatoes',
      'Hill soil around plants',
      'Harvest in dry conditions'
    ]
  },
  'default': {
    treatment: [
      'Isolate infected plants',
      'Remove affected leaves',
      'Apply appropriate fungicide',
      'Consult local agricultural extension'
    ],
    prevention: [
      'Practice crop rotation',
      'Maintain field sanitation',
      'Use certified seeds',
      'Monitor plants regularly'
    ]
  }
};

// let model: tf.LayersModel | null = null;

export async function loadDiseaseModel(): Promise<boolean> {
  try {
    // In a real implementation, load a pre-trained model
    // For demo, we'll use a mock model
    console.log('Disease detection model ready (demo mode)');
    return true;
  } catch (error) {
    console.error('Failed to load disease model:', error);
    return false;
  }
}

export async function predictDisease(imageFile: File): Promise<DiseasePrediction> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        // Simulate AI prediction with random selection
        // In production, this would use actual TensorFlow.js model inference
        const randomIndex = Math.floor(Math.random() * DISEASE_CLASSES.length);
        const disease = DISEASE_CLASSES[randomIndex];
        const confidence = 0.7 + Math.random() * 0.25;
        
        const isHealthy = disease.includes('Healthy');
        const treatment = TREATMENTS[disease] || TREATMENTS['default'];
        
        resolve({
          disease: isHealthy ? 'Healthy Plant' : disease,
          confidence: Math.round(confidence * 100),
          description: isHealthy 
            ? 'The plant appears to be healthy with no signs of disease.'
            : `Detected ${disease}. This is a common plant disease that requires attention.`,
          treatment: isHealthy ? ['Continue regular care and monitoring'] : treatment.treatment,
          prevention: treatment.prevention
        });
      };
      img.src = reader.result as string;
    };
    
    reader.readAsDataURL(imageFile);
  });
}

export function getSupportedCrops(): string[] {
  return ['Apple', 'Blueberry', 'Cherry', 'Corn', 'Grape', 'Orange', 'Peach', 'Pepper', 'Potato', 'Raspberry', 'Soybean', 'Squash', 'Strawberry', 'Tomato'];
}
