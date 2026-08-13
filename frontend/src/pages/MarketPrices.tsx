import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, Search, ArrowUpRight, ArrowDownRight, MapPin } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { CommodityPrice } from '../types';
import { fetchMarketPrices, predictPriceTrend, SUPPORTED_CROPS, translateCropName, translateUnit } from '../services/marketApi';
import { useLanguage } from '../contexts/LanguageContext';

export default function MarketPrices() {
  const { language, t } = useLanguage();
  const [prices, setPrices] = useState<CommodityPrice[]>([]);
  const [filteredPrices, setFilteredPrices] = useState<CommodityPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCommodity, setSelectedCommodity] = useState<CommodityPrice | null>(null);
  const [selectedCropFilter, setSelectedCropFilter] = useState<string>('All');

  useEffect(() => {
    loadPrices();
  }, []);

  useEffect(() => {
    filterPrices();
  }, [searchTerm, prices, selectedCropFilter, language]);

  async function loadPrices() {
    setLoading(true);
    try {
      const data = await fetchMarketPrices();
      setPrices(data);
      setFilteredPrices(data);
      if (data.length > 0) {
        setSelectedCommodity(data[0]);
      }
    } catch (error) {
      console.error('Error loading prices:', error);
    } finally {
      setLoading(false);
    }
  }

  function filterPrices() {
    let filtered = prices;
    if (selectedCropFilter !== 'All') {
      filtered = filtered.filter(p => p.name === selectedCropFilter);
    }
    if (searchTerm.trim()) {
      filtered = filtered.filter(p =>
        translateCropName(p.name, language).toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    setFilteredPrices(filtered);
  }

  function getPrediction(commodity: CommodityPrice) {
    return predictPriceTrend(commodity.history);
  }

  function getTrendText(trend: 'increase' | 'decrease' | 'stable'): string {
    if (trend === 'increase') return t('market.trendIncrease');
    if (trend === 'decrease') return t('market.trendDecrease');
    return t('market.trendStable');
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('market.title')}</h1>
          <p className="text-gray-500">{t('market.subtitle')}</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <select
            value={selectedCropFilter}
            onChange={(e) => setSelectedCropFilter(e.target.value)}
            className="input-field w-44"
          >
            <option value="All">{t('market.allCrops')}</option>
            {SUPPORTED_CROPS.map(crop => (
              <option key={crop} value={crop}>{translateCropName(crop, language)}</option>
            ))}
          </select>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder={t('market.searchPlaceholder')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 w-48"
            />
          </div>
        </div>
      </div>

      {/* Price Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredPrices.map((item) => {
          const prediction = getPrediction(item);
          const isPositive = item.change >= 0;
          const translatedName = translateCropName(item.name, language);
          const translatedUnit = translateUnit(item.unit, language);
          
          return (
            <button
              key={item.name}
              onClick={() => setSelectedCommodity(item)}
              className={`card text-left transition-all hover:shadow-lg ${
                selectedCommodity?.name === item.name ? 'ring-2 ring-primary-500 bg-primary-50/10' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900">{translatedName}</h3>
                {isPositive ? (
                  <TrendingUp className="w-5 h-5 text-green-500" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-500" />
                )}
              </div>
              <p className="text-2xl font-bold text-gray-900">₹{item.currentPrice.toLocaleString()}</p>
              <p className="text-xs text-gray-500">{translatedUnit}</p>
              <div className={`flex items-center gap-1 mt-2 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                <span>{isPositive ? '+' : ''}{item.changePercent.toFixed(2)}%</span>
                <span className="text-gray-400 text-xs">{t('market.fromLastWeek')}</span>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500">{t('market.sevenDayTrend')}</p>
                <div className="flex items-center gap-2">
                  {prediction.trend === 'increase' ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : prediction.trend === 'decrease' ? (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  ) : (
                    <Minus className="w-4 h-4 text-gray-500" />
                  )}
                  <p className={`font-semibold text-sm ${
                    prediction.trend === 'increase' ? 'text-green-600' :
                    prediction.trend === 'decrease' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {getTrendText(prediction.trend)}
                  </p>
                  <span className="text-xs text-gray-400">({prediction.confidence}% {t('market.confidence')})</span>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Chart Section */}
      {selectedCommodity && (
        <div className="card">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {translateCropName(selectedCommodity.name, language)} {t('market.priceTrend')}
              </h2>
              <div className="flex items-center gap-2 text-gray-500 mt-1 text-sm">
                <MapPin className="w-4 h-4 text-primary-500" />
                <span>{selectedCommodity.region}</span>
                <span className="text-gray-300">|</span>
                <span>{t('market.last30Days')}</span>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                {t('market.current')}: ₹{selectedCommodity.currentPrice.toLocaleString()}
              </span>
              {(() => {
                const pred = getPrediction(selectedCommodity);
                return (
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    pred.trend === 'increase' ? 'bg-green-100 text-green-700' :
                    pred.trend === 'decrease' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {t('market.sevenDay')}: {pred.trend === 'increase' ? '↑' : pred.trend === 'decrease' ? '↓' : '→'} {getTrendText(pred.trend)}
                  </span>
                );
              })()}
            </div>
          </div>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={selectedCommodity.history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => new Date(date).toLocaleDateString(language === 'kn' ? 'kn-IN' : 'en-US', { month: 'short', day: 'numeric' })}
                  stroke="#9ca3af"
                />
                <YAxis 
                  stroke="#9ca3af"
                  tickFormatter={(value) => `₹${value}`}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => [`₹${value}`, t('market.priceTrend')] }
                  labelFormatter={(date) => new Date(date).toLocaleDateString(language === 'kn' ? 'kn-IN' : 'en-US')}
                />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#22c55e" 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6, fill: '#22c55e' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Market Insights */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">{t('market.high30Day')}</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{Math.max(...selectedCommodity.history.map(h => h.price)).toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">{t('market.low30Day')}</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{Math.min(...selectedCommodity.history.map(h => h.price)).toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">{t('market.avgPrice')}</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{Math.round(selectedCommodity.history.reduce((sum, h) => sum + h.price, 0) / selectedCommodity.history.length).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 7-Day Forecast */}
      {selectedCommodity && (
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">{t('market.forecastTitle')}</h3>
          {(() => {
            const pred = getPrediction(selectedCommodity);
            return (
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                {pred.forecast_7d.map((price, idx) => {
                  const date = new Date();
                  date.setDate(date.getDate() + idx + 1);
                  return (
                    <div key={idx} className="bg-gray-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-500 mb-1">
                        {date.toLocaleDateString(language === 'kn' ? 'kn-IN' : 'en-US', { weekday: 'short', day: 'numeric' })}
                      </p>
                      <p className="font-semibold text-gray-900">₹{price.toLocaleString()}</p>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>
      )}

      {/* Selling Recommendations */}
      <div className="card bg-amber-50 border-amber-200">
        <h3 className="font-semibold text-amber-900 mb-2">{t('market.insightsTitle')}</h3>
        <ul className="space-y-2 text-amber-800 text-sm">
          <li>{t('market.rec1')}</li>
          <li>{t('market.rec2')}</li>
          <li>{t('market.rec3')}</li>
          <li>{t('market.rec4')}</li>
        </ul>
      </div>
    </div>
  );
}
