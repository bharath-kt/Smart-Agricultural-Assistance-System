const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface DiseaseHistoryItem {
  id: number;
  crop_type?: string;
  detected_disease: string;
  confidence_score: number;
  image_path: string;
  alternative_diseases?: string[];
  created_at: string;
}

export interface SchemeHistoryItem {
  id: number;
  scheme_id?: number;
  scheme_name?: string;
  search_query?: string;
  action_type: string;
  eligibility_status?: string;
  details?: any;
  created_at: string;
}

export interface WeatherHistoryItem {
  id: number;
  location_name: string;
  temperature?: number;
  humidity?: number;
  weather_condition?: string;
  summary_text?: string;
  created_at: string;
}

export interface MarketHistoryItem {
  id: number;
  crop_name: string;
  state?: string;
  district?: string;
  market_name?: string;
  modal_price?: number;
  trend?: string;
  summary_text?: string;
  created_at: string;
}

export interface ActivityLogItem {
  id: number;
  activity_type: string;
  title: string;
  description?: string;
  meta_data?: any;
  created_at: string;
}

export interface FarmerCombinedHistory {
  farmer_id: number;
  disease_history: DiseaseHistoryItem[];
  scheme_history: SchemeHistoryItem[];
  weather_history: WeatherHistoryItem[];
  market_history: MarketHistoryItem[];
  recent_activities: ActivityLogItem[];
}

export const historyApi = {
  async getCombinedHistory(token: string): Promise<FarmerCombinedHistory> {
    const res = await fetch(`${API_BASE_URL}/history/all`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to fetch activity history');
    return res.json();
  },

  async getDiseaseHistory(token: string): Promise<DiseaseHistoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/history/disease`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to fetch disease history');
    return res.json();
  },

  async getSchemeHistory(token: string): Promise<SchemeHistoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/history/schemes`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to fetch scheme history');
    return res.json();
  },

  async clearAllHistory(token: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/history/all`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to clear history');
  },

  async deleteHistoryItem(token: string, category: 'disease' | 'schemes' | 'weather' | 'market', id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/history/${category}/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to delete history item');
  }
};
