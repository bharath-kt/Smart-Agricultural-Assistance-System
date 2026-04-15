import type { CommodityPrice, PriceHistory } from '../types';

// Using mock data since real agricultural APIs often require authentication
export async function fetchMarketPrices(region?: string): Promise<CommodityPrice[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const commodities: CommodityPrice[] = [
    {
      name: 'Wheat',
      currentPrice: 2450,
      previousPrice: 2380,
      change: 70,
      changePercent: 2.94,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(2450, 2100, 2600)
    },
    {
      name: 'Rice (Basmati)',
      currentPrice: 3850,
      previousPrice: 3900,
      change: -50,
      changePercent: -1.28,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(3850, 3500, 4200)
    },
    {
      name: 'Cotton',
      currentPrice: 7200,
      previousPrice: 6950,
      change: 250,
      changePercent: 3.60,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(7200, 6500, 7800)
    },
    {
      name: 'Sugarcane',
      currentPrice: 315,
      previousPrice: 310,
      change: 5,
      changePercent: 1.61,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(315, 280, 340)
    },
    {
      name: 'Maize',
      currentPrice: 2100,
      previousPrice: 2050,
      change: 50,
      changePercent: 2.44,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(2100, 1800, 2400)
    },
    {
      name: 'Soybean',
      currentPrice: 4200,
      previousPrice: 4350,
      change: -150,
      changePercent: -3.45,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(4200, 3800, 4600)
    },
    {
      name: 'Potato',
      currentPrice: 1250,
      previousPrice: 1400,
      change: -150,
      changePercent: -10.71,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(1250, 1000, 1800)
    },
    {
      name: 'Tomato',
      currentPrice: 2800,
      previousPrice: 2200,
      change: 600,
      changePercent: 27.27,
      unit: 'per quintal',
      region: region || 'National Average',
      history: generatePriceHistory(2800, 1500, 3500)
    }
  ];

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

export function predictPriceTrend(history: PriceHistory[]): { prediction: number; confidence: number } {
  if (history.length < 7) {
    return { prediction: 0, confidence: 0 };
  }

  const recent = history.slice(-7);
  const avgChange = recent.reduce((sum, item, idx) => {
    if (idx === 0) return 0;
    return sum + (item.price - recent[idx - 1].price);
  }, 0) / 6;

  const lastPrice = recent[recent.length - 1].price;
  const predictedPrice = Math.round(lastPrice + avgChange * 3);
  const confidence = Math.min(85, Math.max(40, 100 - Math.abs(avgChange) * 2));

  return { prediction: predictedPrice, confidence };
}
