import { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Cloud,
  Sun,
  CloudRain,
  Wind,
  Droplets,
  Thermometer,
  CloudSnow,
  CloudLightning,
  MapPin,
  Loader2,
  AlertCircle,
  RefreshCw,
  Navigation,
} from 'lucide-react';
import type { WeatherData } from '../types';
import {
  fetchWeatherBySearch,
  fetchWeatherByCoords,
  geocodeLocation,
  type GeocodeResult,
} from '../services/weatherApi';
import { useLanguage } from '../contexts/LanguageContext';

const weatherIcons: { [key: string]: React.ElementType } = {
  '01d': Sun,
  '01n': Sun,
  '02d': Cloud,
  '02n': Cloud,
  '03d': Cloud,
  '03n': Cloud,
  '04d': Cloud,
  '04n': Cloud,
  '09d': CloudRain,
  '09n': CloudRain,
  '10d': CloudRain,
  '10n': CloudRain,
  '11d': CloudLightning,
  '11n': CloudLightning,
  '13d': CloudSnow,
  '13n': CloudSnow,
  '50d': Cloud,
  '50n': Cloud,
};

export default function Weather() {
  const { language, t } = useLanguage();
  const [city, setCity] = useState('bengaluru');
  const [searchInput, setSearchInput] = useState('');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isLocating, setIsLocating] = useState(false);
  const [locationError, setLocationError] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState<GeocodeResult[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const loadWeather = useCallback(
    async (targetCity: string, source: 'search' | 'coords' = 'search') => {
      setLoading(true);
      setError('');
      setLocationError('');
      try {
        let data: WeatherData;
        if (source === 'coords') {
          const [lat, lon] = targetCity.split(',').map(Number);
          data = await fetchWeatherByCoords(lat, lon);
          setCity(data.location);
        } else {
          data = await fetchWeatherBySearch(targetCity);
          setCity(data.location);
        }
        setWeather(data);
      } catch (err: any) {
        console.error('Weather load error:', err);
        setError(err.message || t('weather.errorTitle'));
      } finally {
        setLoading(false);
      }
    },
    [t]
  );

  useEffect(() => {
    loadWeather('bengaluru', 'search');
  }, [loadWeather]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (searchInput.trim()) {
      setShowSuggestions(false);
      loadWeather(searchInput.trim(), 'search');
    }
  }

  function handleSuggestionClick(suggestion: GeocodeResult) {
    setSearchInput(suggestion.name);
    setShowSuggestions(false);
    loadWeather(suggestion.name, 'search');
  }

  async function handleSearchInputChange(value: string) {
    setSearchInput(value);
    if (value.length >= 3) {
      try {
        const results = await geocodeLocation(value);
        setSearchSuggestions(results.slice(0, 5));
        setShowSuggestions(true);
      } catch {
        setShowSuggestions(false);
      }
    } else {
      setShowSuggestions(false);
    }
  }

  function handleUseCurrentLocation() {
    if (!navigator.geolocation) {
      setLocationError(t('weather.geoNotSupported'));
      return;
    }
    setIsLocating(true);
    setLocationError('');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setIsLocating(false);
        loadWeather(`${latitude},${longitude}`, 'coords');
      },
      (err) => {
        setIsLocating(false);
        switch (err.code) {
          case err.PERMISSION_DENIED:
            setLocationError(t('weather.deniedError'));
            break;
          case err.POSITION_UNAVAILABLE:
            setLocationError(t('weather.unavailError'));
            break;
          case err.TIMEOUT:
            setLocationError(t('weather.timeoutError'));
            break;
          default:
            setLocationError(t('weather.unableError'));
        }
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
    );
  }

  function getWeatherIcon(iconCode: string) {
    return weatherIcons[iconCode] || Cloud;
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString(language === 'kn' ? 'kn-IN' : 'en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  }

  const CurrentIcon = weather ? getWeatherIcon(weather.icon) : Cloud;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('weather.title')}</h1>
          <p className="text-gray-500">{t('weather.subtitle')}</p>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2 relative">
          <div className="relative">
            <input
              type="text"
              placeholder={t('weather.searchPlaceholder')}
              value={searchInput}
              onChange={(e) => handleSearchInputChange(e.target.value)}
              onFocus={() => searchSuggestions.length > 0 && setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              className="input-field w-56 pr-3"
            />
            {showSuggestions && searchSuggestions.length > 0 && (
              <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-48 overflow-auto">
                {searchSuggestions.map((s, i) => (
                  <button
                    key={i}
                    type="button"
                    onMouseDown={() => handleSuggestionClick(s)}
                    className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm"
                  >
                    <span className="font-medium">{s.name}</span>
                    {s.state && (
                      <span className="text-gray-500 ml-1">, {s.state}</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
          <button type="submit" className="btn-primary flex items-center gap-2">
            <Search className="w-4 h-4" />
            <span className="hidden sm:inline">{t('weather.searchBtn')}</span>
          </button>
          <button
            type="button"
            onClick={handleUseCurrentLocation}
            disabled={isLocating}
            className="btn-secondary flex items-center gap-2"
            title={t('weather.gpsBtn')}
          >
            {isLocating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-xs font-semibold">{language === 'kn' ? 'ಸ್ಥಳ ಪತ್ತೆ ಮಾಡಲಾಗುತ್ತಿದೆ...' : 'Detecting location...'}</span>
              </>
            ) : (
              <>
                <Navigation className="w-4 h-4" />
                <span className="hidden sm:inline">{t('weather.gpsBtn')}</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Location / Status Bar */}
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <MapPin className="w-4 h-4 text-primary-500" />
        <span className="font-medium">{city}</span>
        {weather?.icon && (
          <span className="text-gray-400">· {t('weather.updatedJustNow')}</span>
        )}
      </div>

      {/* Location Error */}
      {locationError && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-amber-800 text-sm">{locationError}</p>
            <p className="text-amber-600 text-xs mt-1">
              {t('weather.locationHint')}
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-10 h-10 text-primary-500 animate-spin mb-3" />
          <p className="text-gray-500">{t('weather.loadingMsg')}</p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h3 className="text-red-800 font-semibold mb-1">{t('weather.errorTitle')}</h3>
          <p className="text-red-600 text-sm mb-4">{error}</p>
          <button
            onClick={() => loadWeather(city, 'search')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            {t('weather.retryBtn')}
          </button>
        </div>
      )}

      {/* Weather Content */}
      {!loading && !error && weather && (
        <>
          {/* Current Weather */}
          <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <h2 className="text-3xl font-bold">{weather.location}</h2>
                <p className="text-blue-100 capitalize text-lg">{weather.description}</p>
                <div className="flex items-center gap-2 mt-4">
                  <CurrentIcon className="w-16 h-16" />
                  <span className="text-5xl font-bold">{weather.temperature}°C</span>
                </div>
                {weather.feelsLike !== weather.temperature && (
                  <p className="text-blue-100 text-sm mt-1">
                    {t('weather.feelsLikeLabel')} {weather.feelsLike}°C
                  </p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Thermometer className="w-5 h-5" />
                    <span className="text-blue-100">{t('weather.feelsLikeLabel')}</span>
                  </div>
                  <p className="text-2xl font-bold">{weather.feelsLike}°C</p>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Droplets className="w-5 h-5" />
                    <span className="text-blue-100">{t('weather.humidityLabel')}</span>
                  </div>
                  <p className="text-2xl font-bold">{weather.humidity}%</p>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Wind className="w-5 h-5" />
                    <span className="text-blue-100">{t('weather.windSpeedLabel')}</span>
                  </div>
                  <p className="text-2xl font-bold">{weather.windSpeed} km/h</p>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <CloudRain className="w-5 h-5" />
                    <span className="text-blue-100">{t('weather.forecastLabel')}</span>
                  </div>
                  <p className="text-2xl font-bold">5 {language === 'kn' ? 'ದಿನಗಳು' : 'Days'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* 5-Day Forecast */}
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-4">{t('weather.fiveDaysForecast')}</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {weather.forecast.map((day, index) => {
                const DayIcon = getWeatherIcon(day.icon);
                return (
                  <div key={index} className="card text-center hover:shadow-md transition-shadow">
                    <p className="text-sm text-gray-500 mb-2">{formatDate(day.date)}</p>
                    <DayIcon className="w-10 h-10 mx-auto mb-2 text-primary-500" />
                    <p className="text-2xl font-bold text-gray-900">{day.temp}°C</p>
                    <p className="text-xs text-gray-500 capitalize mt-1">{day.description}</p>
                    <div className="flex items-center justify-center gap-1 mt-2 text-xs text-blue-500">
                      <Droplets className="w-3 h-3" />
                      <span>{day.humidity}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Farming Tips */}
          <div className="card bg-green-50 border-green-200">
            <h3 className="font-semibold text-green-900 mb-2">
              {t('weather.farmingTipsTitle')}
            </h3>
            <ul className="space-y-2 text-green-800 text-sm">
              {weather.temperature > 30 ? (
                <li>{t('weather.highTempTip')}</li>
              ) : weather.temperature < 20 ? (
                <li>{t('weather.coolTempTip')}</li>
              ) : (
                <li>{t('weather.modTempTip')}</li>
              )}
              {weather.humidity > 70 ? (
                <li>{t('weather.highHumidTip')}</li>
              ) : (
                <li>{t('weather.normHumidTip')}</li>
              )}
              {weather.windSpeed > 20 ? (
                <li>{t('weather.strongWindTip')}</li>
              ) : null}
            </ul>
          </div>
        </>
      )}

      {/* Empty state when no weather and no error */}
      {!loading && !error && !weather && (
        <div className="text-center py-16">
          <Cloud className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">{t('weather.emptyState')}</p>
        </div>
      )}
    </div>
  );
}
