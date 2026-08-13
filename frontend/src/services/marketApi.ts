import type { CommodityPrice, PriceHistory } from '../types';

export const SUPPORTED_CROPS = [
  'Corn', 'Coconut', 'Onion', 'Ginger', 'Tomato', 'Potato', 'Rice',
  'Wheat', 'Banana', 'Chilli', 'Turmeric', 'Sugarcane', 'Groundnut'
];

export const CROP_TRANSLATIONS: Record<string, { en: string; kn: string }> = {
  Corn: { en: 'Corn (Maize)', kn: 'ಮೆಕ್ಕೆಜೋಳ' },
  Coconut: { en: 'Coconut', kn: 'ತೆಂಗಿನಕಾಯಿ' },
  Onion: { en: 'Onion', kn: 'ಈರುಳ್ಳಿ' },
  Ginger: { en: 'Ginger', kn: 'ಶುಂಠಿ' },
  Tomato: { en: 'Tomato', kn: 'ಟೊಮೆಟೊ' },
  Potato: { en: 'Potato', kn: 'ಆಲೂಗಡ್ಡೆ' },
  Rice: { en: 'Rice (Paddy)', kn: 'ಅಕ್ಕಿ / ಭತ್ತ' },
  Wheat: { en: 'Wheat', kn: 'ಗೋಧಿ' },
  Banana: { en: 'Banana', kn: 'ಬಾಳೆಹಣ್ಣು' },
  Chilli: { en: 'Chilli', kn: 'ಮೆಣಸಿನಕಾಯಿ' },
  Turmeric: { en: 'Turmeric', kn: 'ಅರಿಶಿನ' },
  Sugarcane: { en: 'Sugarcane', kn: 'ಕಬ್ಬು' },
  Groundnut: { en: 'Groundnut', kn: 'ಕಡಲೆಕಾಯಿ' }
};

export const UNIT_TRANSLATIONS: Record<string, { en: string; kn: string }> = {
  'per quintal': { en: 'per quintal', kn: 'ಪ್ರತಿ ಕ್ವಿಂಟಾಲ್‌ಗೆ' },
  'per 100 nuts': { en: 'per 100 nuts', kn: 'ಪ್ರತಿ 100 ಕಾಯಿಗಳಿಗೆ' }
};

export function translateCropName(cropName: string, lang: string): string {
  if (lang === 'kn' && CROP_TRANSLATIONS[cropName]) {
    return CROP_TRANSLATIONS[cropName].kn;
  }
  return CROP_TRANSLATIONS[cropName]?.en || cropName;
}

export function translateUnit(unit: string, lang: string): string {
  if (lang === 'kn' && UNIT_TRANSLATIONS[unit]) {
    return UNIT_TRANSLATIONS[unit].kn;
  }
  return UNIT_TRANSLATIONS[unit]?.en || unit;
}

// Realistic Indian market prices (per quintal or per unit)
const CROP_DATA: { [key: string]: { current: number; min: number; max: number; unit: string } } = {
  Corn: { current: 2100, min: 1850, max: 2400, unit: 'per quintal' },
  Coconut: { current: 2500, min: 1800, max: 3200, unit: 'per 100 nuts' },
  Onion: { current: 2200, min: 1200, max: 4000, unit: 'per quintal' },
  Ginger: { current: 8500, min: 6000, max: 12000, unit: 'per quintal' },
  Tomato: { current: 2800, min: 1500, max: 4500, unit: 'per quintal' },
  Potato: { current: 1400, min: 900, max: 2000, unit: 'per quintal' },
  Rice: { current: 3600, min: 3000, max: 4500, unit: 'per quintal' },
  Wheat: { current: 2450, min: 2100, max: 2700, unit: 'per quintal' },
  Banana: { current: 1800, min: 1200, max: 2500, unit: 'per quintal' },
  Chilli: { current: 12000, min: 8000, max: 18000, unit: 'per quintal' },
  Turmeric: { current: 9500, min: 7000, max: 13000, unit: 'per quintal' },
  Sugarcane: { current: 340, min: 290, max: 380, unit: 'per quintal' },
  Groundnut: { current: 5800, min: 4800, max: 7000, unit: 'per quintal' }
};

export async function fetchMarketPrices(region?: string, cropName?: string): Promise<CommodityPrice[]> {
  // Try logging query to backend API if token exists
  const token = localStorage.getItem('smart_agri_token');
  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  if (token && cropName) {
    try {
      fetch(`${apiBase}/market/prices?crop_name=${encodeURIComponent(cropName)}`, {
        headers: { Authorization: `Bearer ${token}` }
      }).catch(() => {});
    } catch (e) {
      // ignore
    }
  }

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));

  const commodities: CommodityPrice[] = SUPPORTED_CROPS.map(name => {
    const data = CROP_DATA[name];
    const prevPrice = Math.round(data.current * (0.95 + Math.random() * 0.1));
    const change = data.current - prevPrice;
    const changePercent = parseFloat(((change / prevPrice) * 100).toFixed(2));

    return {
      name,
      currentPrice: data.current,
      previousPrice: prevPrice,
      change,
      changePercent,
      unit: data.unit,
      region: region || 'Karnataka, India',
      history: generatePriceHistory(data.current, data.min, data.max)
    };
  });

  return commodities;
}

function generatePriceHistory(current: number, min: number, max: number): PriceHistory[] {
  const history: PriceHistory[] = [];
  const today = new Date();
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Generate realistic price movement
    const trend = (30 - i) / 30;
    const randomVariation = (Math.random() - 0.5) * (max - min) * 0.1;
    const trendPrice = min + (current - min) * trend;
    const price = Math.round(Math.max(min, Math.min(max, trendPrice + randomVariation)));
    
    history.push({
      date: date.toISOString().split('T')[0],
      price
    });
  }
  
  return history;
}

export interface PricePrediction {
  prediction: number;
  confidence: number;
  forecast_7d: number[];
  trend: 'increase' | 'decrease' | 'stable';
}

export function predictPriceTrend(history: PriceHistory[]): PricePrediction {
  if (history.length < 7) {
    return { prediction: 0, confidence: 0, forecast_7d: [], trend: 'stable' };
  }

  const recent = history.slice(-7);
  const avgChange = recent.reduce((sum, item, idx) => {
    if (idx === 0) return 0;
    return sum + (item.price - recent[idx - 1].price);
  }, 0) / 6;

  const lastPrice = recent[recent.length - 1].price;
  const forecast_7d: number[] = [];
  let currentPrice = lastPrice;

  for (let i = 0; i < 7; i++) {
    currentPrice = Math.round(currentPrice + avgChange + (Math.random() - 0.5) * Math.abs(avgChange));
    forecast_7d.push(currentPrice);
  }

  const predictedPrice = forecast_7d[forecast_7d.length - 1];
  const confidence = Math.min(85, Math.max(40, 100 - Math.abs(avgChange) * 2));

  let trend: 'increase' | 'decrease' | 'stable' = 'stable';
  if (predictedPrice > lastPrice * 1.02) trend = 'increase';
  else if (predictedPrice < lastPrice * 0.98) trend = 'decrease';

  return { prediction: predictedPrice, confidence, forecast_7d, trend };
}
