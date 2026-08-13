const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface FarmerProfileData {
  user_id: number;
  full_name?: string;
  email?: string;
  mobile_number?: string;
  age?: number;
  gender?: string;
  state?: string;
  district?: string;
  farmer_category?: string;
  land_ownership?: string;
  land_size?: number;
  crops_grown: string[];
  annual_income?: number;
  irrigation_type?: string;
  farming_type?: string;
  additional_info?: string;
  updated_at?: string;
}

export const profileApi = {
  async getProfile(token: string): Promise<FarmerProfileData> {
    const res = await fetch(`${API_BASE_URL}/profile`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to fetch profile');
    return res.json();
  },

  async updateProfile(token: string, data: Partial<FarmerProfileData>): Promise<FarmerProfileData> {
    const res = await fetch(`${API_BASE_URL}/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  }
};
