// Weather Types
export interface WeatherData {
  location: string;
  temperature: number;
  feelsLike: number;
  humidity: number;
  windSpeed: number;
  description: string;
  icon: string;
  forecast: ForecastDay[];
}

export interface ForecastDay {
  date: string;
  temp: number;
  description: string;
  icon: string;
  humidity: number;
}

// Market Price Types
export interface CommodityPrice {
  name: string;
  currentPrice: number;
  previousPrice: number;
  change: number;
  changePercent: number;
  unit: string;
  region: string;
  history: PriceHistory[];
}

export interface PriceHistory {
  date: string;
  price: number;
}

// Government Scheme Types
export interface GovernmentScheme {
  id: string;
  title: string;
  description: string;
  category: 'subsidy' | 'loan' | 'insurance' | 'training' | 'equipment';
  eligibility: string[];
  benefits: string;
  applicationProcess: string;
  documents: string[];
  deadline?: string;
  website?: string;
}

// Disease Detection Types
export interface DiseasePrediction {
  plantName: string;
  diseaseName: string;
  disease: string;
  confidence: number;
  description: string;
  treatment: string[];
  prevention: string[];
}

export interface UploadedImage {
  file: File;
  preview: string;
}

// Navigation
export interface NavItem {
  path: string;
  label: string;
  icon: string;
}
