import type { WeatherData, ForecastDay } from '../types';

const API_KEY = import.meta.env.VITE_OPENWEATHER_API_KEY || '';
const BASE_URL = 'https://api.openweathermap.org/data/2.5';

export async function fetchWeatherData(city: string): Promise<WeatherData> {
  // For demo purposes, return mock data if no API key
  if (!API_KEY) {
    return getMockWeatherData(city);
  }

  try {
    const [currentRes, forecastRes] = await Promise.all([
      fetch(`${BASE_URL}/weather?q=${city}&appid=${API_KEY}&units=metric`),
      fetch(`${BASE_URL}/forecast?q=${city}&appid=${API_KEY}&units=metric`)
    ]);

    if (!currentRes.ok || !forecastRes.ok) {
      throw new Error('Failed to fetch weather data');
    }

    const current = await currentRes.json();
    const forecast = await forecastRes.json();

    return {
      location: current.name,
      temperature: Math.round(current.main.temp),
      feelsLike: Math.round(current.main.feels_like),
      humidity: current.main.humidity,
      windSpeed: current.wind.speed,
      description: current.weather[0].description,
      icon: current.weather[0].icon,
      forecast: processForecast(forecast.list)
    };
  } catch (error) {
    console.error('Weather API error:', error);
    return getMockWeatherData(city);
  }
}

function processForecast(list: any[]): ForecastDay[] {
  const daily: { [key: string]: any[] } = {};
  
  list.forEach((item) => {
    const date = item.dt_txt.split(' ')[0];
    if (!daily[date]) daily[date] = [];
    daily[date].push(item);
  });

  return Object.entries(daily)
    .slice(0, 5)
    .map(([date, items]) => {
      const avg = items.reduce((sum, item) => sum + item.main.temp, 0) / items.length;
      const midday = items[Math.floor(items.length / 2)];
      return {
        date,
        temp: Math.round(avg),
        description: midday.weather[0].description,
        icon: midday.weather[0].icon,
        humidity: Math.round(items.reduce((sum, item) => sum + item.main.humidity, 0) / items.length)
      };
    });
}

function getMockWeatherData(city: string): WeatherData {
  return {
    location: city || 'New Delhi',
    temperature: 32,
    feelsLike: 35,
    humidity: 65,
    windSpeed: 12,
    description: 'partly cloudy',
    icon: '02d',
    forecast: [
      { date: '2024-01-16', temp: 33, description: 'sunny', icon: '01d', humidity: 60 },
      { date: '2024-01-17', temp: 31, description: 'cloudy', icon: '03d', humidity: 70 },
      { date: '2024-01-18', temp: 30, description: 'light rain', icon: '10d', humidity: 75 },
      { date: '2024-01-19', temp: 32, description: 'sunny', icon: '01d', humidity: 55 },
      { date: '2024-01-20', temp: 34, description: 'sunny', icon: '01d', humidity: 50 },
    ]
  };
}
