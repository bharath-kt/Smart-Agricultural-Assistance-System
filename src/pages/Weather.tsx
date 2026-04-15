import { useState, useEffect } from 'react';
import { Search, Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, CloudSnow, CloudLightning } from 'lucide-react';
import type { WeatherData } from '../types';
import { fetchWeatherData } from '../services/weatherApi';

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
  const [city, setCity] = useState('New Delhi');
  const [searchInput, setSearchInput] = useState('');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadWeather();
  }, [city]);

  async function loadWeather() {
    setLoading(true);
    setError('');
    try {
      const data = await fetchWeatherData(city);
      setWeather(data);
    } catch (err) {
      setError('Failed to load weather data');
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (searchInput.trim()) {
      setCity(searchInput.trim());
    }
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  }

  function getWeatherIcon(iconCode: string) {
    return weatherIcons[iconCode] || Cloud;
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error || !weather) {
    return (
      <div className="text-center py-12">
        <Cloud className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">{error || 'No weather data available'}</p>
        <button onClick={loadWeather} className="btn-primary mt-4">Retry</button>
      </div>
    );
  }

  const CurrentIcon = getWeatherIcon(weather.icon);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Weather Monitoring</h1>
          <p className="text-gray-500">Real-time weather updates for your farm</p>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search city..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="input-field w-48"
          />
          <button type="submit" className="btn-primary flex items-center gap-2">
            <Search className="w-4 h-4" />
            <span className="hidden sm:inline">Search</span>
          </button>
        </form>
      </div>

      {/* Current Weather */}
      <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h2 className="text-3xl font-bold">{weather.location}</h2>
            <p className="text-blue-100 capitalize text-lg">{weather.description}</p>
            <div className="flex items-center gap-2 mt-4">
              <CurrentIcon className="w-16 h-16" />
              <span className="text-5xl font-bold">{weather.temperature}°C</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-1">
                <Thermometer className="w-5 h-5" />
                <span className="text-blue-100">Feels Like</span>
              </div>
              <p className="text-2xl font-bold">{weather.feelsLike}°C</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-1">
                <Droplets className="w-5 h-5" />
                <span className="text-blue-100">Humidity</span>
              </div>
              <p className="text-2xl font-bold">{weather.humidity}%</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-1">
                <Wind className="w-5 h-5" />
                <span className="text-blue-100">Wind Speed</span>
              </div>
              <p className="text-2xl font-bold">{weather.windSpeed} km/h</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-1">
                <CloudRain className="w-5 h-5" />
                <span className="text-blue-100">Forecast</span>
              </div>
              <p className="text-2xl font-bold">5 Days</p>
            </div>
          </div>
        </div>
      </div>

      {/* 5-Day Forecast */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">5-Day Forecast</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {weather.forecast.map((day, index) => {
            const DayIcon = getWeatherIcon(day.icon);
            return (
              <div key={index} className="card text-center">
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
        <h3 className="font-semibold text-green-900 mb-2">Farming Tips for Current Weather</h3>
        <ul className="space-y-2 text-green-800">
          {weather.temperature > 30 ? (
            <li>• High temperature expected. Ensure adequate irrigation for crops.</li>
          ) : weather.temperature < 20 ? (
            <li>• Cool weather. Good conditions for wheat and other winter crops.</li>
          ) : (
            <li>• Moderate temperature. Ideal for most crop activities.</li>
          )}
          {weather.humidity > 70 ? (
            <li>• High humidity may increase disease risk. Monitor crops closely.</li>
          ) : (
            <li>• Normal humidity levels. Continue regular crop monitoring.</li>
          )}
          {weather.windSpeed > 20 ? (
            <li>• Strong winds expected. Secure any loose structures or covers.</li>
          ) : null}
        </ul>
      </div>
    </div>
  );
}
