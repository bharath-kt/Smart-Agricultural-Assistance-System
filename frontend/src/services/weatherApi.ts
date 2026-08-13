import type { WeatherData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  const token = localStorage.getItem('smart_agri_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

class WeatherAPIError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = 'WeatherAPIError';
    this.status = status;
  }
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getHeaders(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let message = `HTTP error! status: ${response.status}`;
    try {
      const errorData = await response.json();
      message = errorData.detail || message;
    } catch {
      // ignore parse error
    }
    throw new WeatherAPIError(message, response.status);
  }

  return response.json();
}

export interface GeocodeResult {
  name: string;
  lat: number;
  lon: number;
  country: string;
  state?: string;
}

export interface CombinedWeather {
  location: {
    name: string;
    country: string;
    latitude: number;
    longitude: number;
  };
  current: {
    location: { name: string; country: string; latitude: number; longitude: number };
    temperature: number;
    feels_like: number;
    humidity: number;
    pressure: number;
    wind_speed: number;
    wind_direction?: number;
    visibility?: number;
    weather_main: string;
    weather_description: string;
    weather_icon?: string;
    timestamp: string;
    source?: string;
  };
  forecast: {
    location: { name: string; country: string; latitude: number; longitude: number };
    forecast: Array<{
      date: string;
      temperature_min: number;
      temperature_max: number;
      humidity: number;
      wind_speed: number;
      precipitation_probability: number;
      weather_main: string;
      weather_description: string;
    }>;
    generated_at: string;
    source?: string;
  };
}

/**
 * Search weather by city name or pincode.
 * Backend handles geocoding and returns current + forecast data.
 */
export async function fetchWeatherBySearch(query: string, days = 5): Promise<WeatherData> {
  const encoded = encodeURIComponent(query);
  const data = await request<CombinedWeather>(
    `${API_BASE_URL}/weather/search?q=${encoded}&days=${days}`
  );
  return mapBackendToFrontend(data);
}

/**
 * Fetch weather by GPS coordinates.
 */
export async function fetchWeatherByCoords(
  latitude: number,
  longitude: number,
  days = 5
): Promise<WeatherData> {
  const data = await request<CombinedWeather>(
    `${API_BASE_URL}/weather/search?lat=${latitude}&lon=${longitude}&days=${days}`
  );
  return mapBackendToFrontend(data);
}

/**
 * Geocode a city name or pincode.
 */
export async function geocodeLocation(query: string): Promise<GeocodeResult[]> {
  const encoded = encodeURIComponent(query);
  return request<GeocodeResult[]>(`${API_BASE_URL}/weather/geocode?q=${encoded}`);
}

/**
 * Convert wind speed from m/s to km/h.
 */
export function windSpeedToKmh(mps: number): number {
  return Math.round(mps * 3.6);
}

function mapBackendToFrontend(data: CombinedWeather): WeatherData {
  const current = data.current;
  const forecast = data.forecast;

  return {
    location: current.location.name,
    temperature: Math.round(current.temperature),
    feelsLike: Math.round(current.feels_like),
    humidity: current.humidity,
    windSpeed: windSpeedToKmh(current.wind_speed),
    description: current.weather_description,
    icon: current.weather_icon || '02d',
    forecast: forecast.forecast.map((day) => ({
      date: day.date,
      temp: Math.round((day.temperature_min + day.temperature_max) / 2),
      description: day.weather_description,
      icon: mapWeatherMainToIcon(day.weather_main),
      humidity: day.humidity,
    })),
  };
}

function mapWeatherMainToIcon(main: string): string {
  const map: Record<string, string> = {
    Clear: '01d',
    Clouds: '03d',
    Rain: '10d',
    Drizzle: '09d',
    Thunderstorm: '11d',
    Snow: '13d',
    Mist: '50d',
    Fog: '50d',
    Haze: '50d',
  };
  return map[main] || '02d';
}
