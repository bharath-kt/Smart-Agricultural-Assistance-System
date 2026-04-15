import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Search, Filter, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { CommodityPrice } from '../types';
import { fetchMarketPrices, predictPriceTrend } from '../services/marketApi';

export default function MarketPrices() {
  const [prices, setPrices] = useState<CommodityPrice[]>([]);
  const [filteredPrices, setFilteredPrices] = useState<CommodityPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCommodity, setSelectedCommodity] = useState<CommodityPrice | null>(null);

  useEffect(() => {
    loadPrices();
  }, []);

  useEffect(() => {
    filterPrices();
  }, [searchTerm, prices]);

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
    if (!searchTerm.trim()) {
      setFilteredPrices(prices);
      return;
    }
    const filtered = prices.filter(p => 
      p.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredPrices(filtered);
  }

  function getPrediction(commodity: CommodityPrice) {
    return predictPriceTrend(commodity.history);
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
          <h1 className="text-2xl font-bold text-gray-900">Market Price Prediction</h1>
          <p className="text-gray-500">Track commodity prices and market trends</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search commodities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 w-48"
            />
          </div>
          <button className="btn-secondary flex items-center gap-2">
            <Filter className="w-4 h-4" />
            <span className="hidden sm:inline">Filter</span>
          </button>
        </div>
      </div>

      {/* Price Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {filteredPrices.map((item) => {
          const prediction = getPrediction(item);
          const isPositive = item.change >= 0;
          
          return (
            <button
              key={item.name}
              onClick={() => setSelectedCommodity(item)}
              className={`card text-left transition-all hover:shadow-lg ${
                selectedCommodity?.name === item.name ? 'ring-2 ring-primary-500' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900">{item.name}</h3>
                {isPositive ? (
                  <TrendingUp className="w-5 h-5 text-green-500" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-500" />
                )}
              </div>
              <p className="text-2xl font-bold text-gray-900">₹{item.currentPrice.toLocaleString()}</p>
              <p className="text-sm text-gray-500">{item.unit}</p>
              <div className={`flex items-center gap-1 mt-2 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                <span>{isPositive ? '+' : ''}{item.changePercent.toFixed(2)}%</span>
                <span className="text-gray-400">from last week</span>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500">Predicted (3 days)</p>
                <p className={`font-semibold ${prediction.prediction > item.currentPrice ? 'text-green-600' : 'text-red-600'}`}>
                  ₹{prediction.prediction.toLocaleString()}
                  <span className="text-xs text-gray-400 ml-1">({prediction.confidence}% confidence)</span>
                </p>
              </div>
            </button>
          );
        })}
      </div>

      {/* Chart Section */}
      {selectedCommodity && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{selectedCommodity.name} Price Trend</h2>
              <p className="text-gray-500">Last 30 days price history</p>
            </div>
            <div className="flex gap-2">
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                Current: ₹{selectedCommodity.currentPrice.toLocaleString()}
              </span>
            </div>
          </div>
          
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={selectedCommodity.history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
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
                  formatter={(value) => [`₹${value}`, 'Price']}
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
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
              <p className="text-sm text-gray-500">30-Day High</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{Math.max(...selectedCommodity.history.map(h => h.price)).toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">30-Day Low</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{Math.min(...selectedCommodity.history.map(h => h.price)).toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500">Average Price</p>
              <p className="text-xl font-bold text-gray-900">
                ₹{Math.round(selectedCommodity.history.reduce((sum, h) => sum + h.price, 0) / selectedCommodity.history.length).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Selling Recommendations */}
      <div className="card bg-amber-50 border-amber-200">
        <h3 className="font-semibold text-amber-900 mb-2">Market Insights</h3>
        <ul className="space-y-2 text-amber-800">
          <li>• Wheat prices are trending upward. Good time to sell if you have surplus stock.</li>
          <li>• Tomato prices have increased significantly due to seasonal demand.</li>
          <li>• Cotton market showing strong growth. Consider holding for better prices.</li>
          <li>• Potato prices have declined. Monitor market before selling.</li>
        </ul>
      </div>
    </div>
  );
}
