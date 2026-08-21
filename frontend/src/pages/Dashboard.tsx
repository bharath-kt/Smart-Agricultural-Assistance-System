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
  Droplets,
  Sprout,
  MapPin,
  Clock,
  User,
  Sparkles
} from 'lucide-react';
import type { WeatherData, CommodityPrice } from '../types';
import { fetchWeatherBySearch } from '../services/weatherApi';
import { fetchMarketPrices, translateCropName } from '../services/marketApi';
import { fetchBackendRecommendations } from '../services/schemesData';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { historyApi, type FarmerCombinedHistory } from '../services/historyApi';

export default function Dashboard() {
  const { language, t } = useLanguage();
  const { isAuthenticated, profile, token, user } = useAuth();

  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [prices, setPrices] = useState<CommodityPrice[]>([]);
  const [recommendations, setRecommendations] = useState<any | null>(null);
  const [userHistory, setUserHistory] = useState<FarmerCombinedHistory | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setUserHistory(null);
    setRecommendations(null);
    loadData();
  }, [isAuthenticated, profile, token, user?.id]);

  async function loadData() {
    setUserHistory(null);
    setRecommendations(null);
    setLoading(true);
    try {
      const searchLocation = profile?.district || profile?.state || 'Mysuru';
      
      const [weatherData, priceData] = await Promise.all([
        fetchWeatherBySearch(searchLocation),
        fetchMarketPrices()
      ]);
      setWeather(weatherData);

      // Filter prices for farmer's saved crops if available
      if (profile?.crops_grown && profile.crops_grown.length > 0) {
        const farmerCropsLower = profile.crops_grown.map(c => c.toLowerCase());
        const filtered = priceData.filter(p => farmerCropsLower.includes(p.name.toLowerCase()));
        setPrices(filtered.length > 0 ? filtered.slice(0, 4) : priceData.slice(0, 4));
      } else {
        setPrices(priceData.slice(0, 4));
      }

      // Fetch backend scheme recommendations & history if logged in
      if (token && isAuthenticated) {
        fetchBackendRecommendations(token)
          .then(rec => setRecommendations(rec))
          .catch(e => console.error('Failed to load scheme recs:', e));

        historyApi.getCombinedHistory(token)
          .then(hist => setUserHistory(hist))
          .catch(e => console.error('Failed to load history:', e));
      } else {
        setRecommendations(null);
        setUserHistory(null);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }

  const features = [
    {
      title: t('dashboard.features.weatherTitle'),
      description: t('dashboard.features.weatherDesc'),
      icon: Cloud,
      path: '/weather',
      color: 'bg-blue-500',
      lightColor: 'bg-blue-50'
    },
    {
      title: t('dashboard.features.marketTitle'),
      description: t('dashboard.features.marketDesc'),
      icon: TrendingUp,
      path: '/market',
      color: 'bg-amber-500',
      lightColor: 'bg-amber-50'
    },
    {
      title: t('dashboard.features.schemesTitle'),
      description: t('dashboard.features.schemesDesc'),
      icon: Building2,
      path: '/schemes',
      color: 'bg-purple-500',
      lightColor: 'bg-purple-50'
    },
    {
      title: t('dashboard.features.diseaseTitle'),
      description: t('dashboard.features.diseaseDesc'),
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
      <div className="bg-gradient-to-r from-primary-600 via-primary-700 to-green-700 rounded-2xl p-6 lg:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                {isAuthenticated ? 'Authenticated Farmer Profile' : 'AgriMitra AI Assistant'}
              </span>
            </div>
            <h1 className="text-2xl lg:text-4xl font-bold">
              {isAuthenticated && user?.full_name
                ? `${language === 'kn' ? 'ಸ್ವಾಗತ' : 'Welcome back'}, ${user.full_name}!`
                : t('dashboard.welcomeTitle')}
            </h1>
            <p className="text-primary-100 text-sm lg:text-base leading-relaxed max-w-2xl">
              {isAuthenticated && profile
                ? `Location: ${profile.district || 'Mysuru'}, ${profile.state || 'Karnataka'} • Farmer Category: ${profile.farmer_category || 'Small'} • Land: ${profile.land_size || 1.5} Ha`
                : t('dashboard.welcomeSubtitle')}
            </p>

            {/* Saved Crops Badges */}
            {profile?.crops_grown && profile.crops_grown.length > 0 && (
              <div className="flex items-center gap-2 pt-2 flex-wrap">
                <span className="text-xs text-primary-200 font-semibold flex items-center gap-1">
                  <Sprout className="w-4 h-4 text-green-300" />
                  {language === 'kn' ? 'ನನ್ನ ಬೆಳೆಗಳು:' : 'My Crops:'}
                </span>
                {profile.crops_grown.map((crop) => (
                  <span key={crop} className="bg-white/15 hover:bg-white/25 px-2.5 py-1 rounded-lg text-xs font-semibold backdrop-blur-sm border border-white/10">
                    {crop}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Quick Action Button */}
          <div className="shrink-0 flex flex-col gap-2">
            {!isAuthenticated ? (
              <Link
                to="/login"
                className="px-6 py-3 bg-white text-primary-700 hover:bg-primary-50 font-bold rounded-xl shadow-lg transition-all text-center text-sm"
              >
                {language === 'kn' ? 'ರೈತರ ಲಾಗಿನ್ / ನೋಂದಣಿ' : 'Farmer Login / Signup'}
              </Link>
            ) : (
              <Link
                to="/profile"
                className="px-5 py-2.5 bg-white/20 hover:bg-white/30 backdrop-blur-md text-white border border-white/30 font-semibold rounded-xl text-xs flex items-center gap-2 transition-all justify-center"
              >
                <User className="w-4 h-4" />
                <span>{language === 'kn' ? 'ಪ್ರೊಫೈಲ್ ತಿದ್ದುಪಡಿ' : 'Edit Farmer Profile'}</span>
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Personalized Scheme Match Banner */}
      {recommendations && (
        <div className="bg-gradient-to-r from-purple-900 to-indigo-800 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 bg-amber-400 text-purple-950 font-bold text-xs rounded-md">
                Eligibility Engine Match
              </span>
              <span className="text-xs text-purple-200">
                Based on saved farmer profile
              </span>
            </div>
            <h3 className="text-xl font-bold">
              {recommendations.eligible_count} Government Schemes Match Your Profile Exactly!
            </h3>
            <p className="text-xs text-purple-200">
              Plus {recommendations.partial_count} additional partially matching schemes available for {profile?.farmer_category || 'Small'} farmers in {profile?.state || 'Karnataka'}.
            </p>
          </div>
          <Link
            to="/schemes"
            className="px-5 py-2.5 bg-amber-400 hover:bg-amber-300 text-purple-950 font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-md transition-all shrink-0"
          >
            <span>View Matched Schemes</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {/* Quick Stats */}
      {weather && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-primary-600" />
              <span>Weather in {profile?.district || 'Mysuru'}, {profile?.state || 'Karnataka'}</span>
            </h2>
            <Link to="/weather" className="text-xs text-primary-600 hover:underline font-semibold">
              Full Forecast →
            </Link>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center shrink-0">
                  <Thermometer className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">{t('dashboard.quickStats.temperature')}</p>
                  <p className="text-xl font-bold text-gray-900">{weather.temperature}°C</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center shrink-0">
                  <Droplets className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">{t('dashboard.quickStats.humidity')}</p>
                  <p className="text-xl font-bold text-gray-900">{weather.humidity}%</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center shrink-0">
                  <Sun className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">{t('dashboard.quickStats.feelsLike')}</p>
                  <p className="text-xl font-bold text-gray-900">{weather.feelsLike}°C</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center shrink-0">
                  <CloudRain className="w-5 h-5 text-cyan-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">{t('dashboard.quickStats.windSpeed')}</p>
                  <p className="text-xl font-bold text-gray-900">{weather.windSpeed} km/h</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">{t('dashboard.quickAccess')}</h2>
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
          <h2 className="text-xl font-bold text-gray-900">
            {profile?.crops_grown ? 'Market Prices (My Crops)' : t('dashboard.marketHighlights')}
          </h2>
          <Link to="/market" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            {t('dashboard.viewAll')}
          </Link>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {prices.map((item) => (
            <div key={item.name} className="card border border-gray-200">
              <p className="text-sm text-gray-500 font-medium">{translateCropName(item.name, language)}</p>
              <p className="text-lg font-bold text-gray-900">₹{item.currentPrice}</p>
              <p className={`text-sm ${item.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {item.change >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity Section */}
      {userHistory && userHistory.recent_activities.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary-600" />
              <span>{language === 'kn' ? 'ಇತ್ತೀಚಿನ ಚಟುವಟಿಕೆಗಳು' : 'Recent Farmer Activity'}</span>
            </h2>
            <Link to="/history" className="text-xs font-semibold text-primary-600 hover:underline">
              View All History →
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {userHistory.recent_activities.slice(0, 3).map((act) => (
              <div key={act.id} className="p-3 bg-gray-50 border border-gray-100 rounded-xl space-y-1">
                <span className="text-[10px] uppercase font-bold text-primary-700 bg-primary-100 px-2 py-0.5 rounded">
                  {act.activity_type}
                </span>
                <p className="text-xs font-bold text-gray-900 truncate">{act.title}</p>
                <p className="text-[11px] text-gray-500 line-clamp-2">{act.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
