import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Cloud, 
  TrendingUp, 
  Building2, 
  ScanLine,
  ArrowRight,
  Sun,
  CloudRain,
  Thermometer,
  Droplets
} from 'lucide-react';
import type { WeatherData, CommodityPrice } from '../types';
import { fetchWeatherData } from '../services/weatherApi';
import { fetchMarketPrices } from '../services/marketApi';
import { governmentSchemes } from '../services/schemesData';

export default function Dashboard() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [prices, setPrices] = useState<CommodityPrice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [weatherData, priceData] = await Promise.all([
        fetchWeatherData('New Delhi'),
        fetchMarketPrices()
      ]);
      setWeather(weatherData);
      setPrices(priceData.slice(0, 4));
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }

  const features = [
    {
      title: 'Weather Monitoring',
      description: 'Real-time weather updates and 5-day forecasts for better crop planning.',
      icon: Cloud,
      path: '/weather',
      color: 'bg-blue-500',
      lightColor: 'bg-blue-50'
    },
    {
      title: 'Market Prices',
      description: 'Track commodity prices and get predictions for better selling decisions.',
      icon: TrendingUp,
      path: '/market',
      color: 'bg-secondary-500',
      lightColor: 'bg-amber-50'
    },
    {
      title: 'Govt Schemes',
      description: 'Discover and apply for government schemes and subsidies.',
      icon: Building2,
      path: '/schemes',
      color: 'bg-purple-500',
      lightColor: 'bg-purple-50'
    },
    {
      title: 'Disease Detection',
      description: 'AI-powered leaf disease detection with treatment recommendations.',
      icon: ScanLine,
      path: '/disease',
      color: 'bg-red-500',
      lightColor: 'bg-red-50'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-6 lg:p-8 text-white">
        <h1 className="text-2xl lg:text-3xl font-bold mb-2">Welcome to Farmer Bot</h1>
        <p className="text-primary-100 text-lg">
          Your intelligent farming assistant for weather, market prices, government schemes, and crop health.
        </p>
      </div>

      {/* Quick Stats */}
      {weather && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <Thermometer className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Temperature</p>
                <p className="text-xl font-bold text-gray-900">{weather.temperature}°C</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Droplets className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Humidity</p>
                <p className="text-xl font-bold text-gray-900">{weather.humidity}%</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Sun className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Feels Like</p>
                <p className="text-xl font-bold text-gray-900">{weather.feelsLike}°C</p>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center">
                <CloudRain className="w-5 h-5 text-cyan-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Wind Speed</p>
                <p className="text-xl font-bold text-gray-900">{weather.windSpeed} km/h</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.path}
                to={feature.path}
                className="group card hover:shadow-lg transition-all duration-200"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 ${feature.lightColor} rounded-xl flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-6 h-6 ${feature.color.replace('bg-', 'text-')}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">{feature.description}</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Market Prices Preview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Market Highlights</h2>
          <Link to="/market" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            View All
          </Link>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {prices.map((item) => (
            <div key={item.name} className="card">
              <p className="text-sm text-gray-500">{item.name}</p>
              <p className="text-lg font-bold text-gray-900">₹{item.currentPrice}</p>
              <p className={`text-sm ${item.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {item.change >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Latest Schemes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Featured Schemes</h2>
          <Link to="/schemes" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            View All
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {governmentSchemes.slice(0, 2).map((scheme) => (
            <div key={scheme.id} className="card">
              <div className="flex items-center gap-2 mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize
                  ${scheme.category === 'subsidy' ? 'bg-green-100 text-green-700' : ''}
                  ${scheme.category === 'loan' ? 'bg-blue-100 text-blue-700' : ''}
                  ${scheme.category === 'insurance' ? 'bg-purple-100 text-purple-700' : ''}
                  ${scheme.category === 'training' ? 'bg-orange-100 text-orange-700' : ''}
                  ${scheme.category === 'equipment' ? 'bg-cyan-100 text-cyan-700' : ''}
                `}>
                  {scheme.category}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{scheme.title}</h3>
              <p className="text-sm text-gray-500 line-clamp-2">{scheme.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
