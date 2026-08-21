const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface SignupPayload {
  full_name: string;
  identifier: string;
  password: string;
  state?: string;
  district?: string;
  farmer_category?: string;
  land_size?: number;
  crops_grown?: string[];
}

export interface LoginPayload {
  identifier: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  full_name?: string;
}

function parseFetchError(err: unknown, fallbackMessage: string): Error {
  if (err instanceof TypeError && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
    return new Error('Unable to connect to the agricultural server. Please check your internet connection or server status.');
  }
  if (err instanceof Error) {
    return err;
  }
  return new Error(fallbackMessage);
}

export const authApi = {
  async signup(data: SignupPayload): Promise<AuthResponse> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Registration failed' }));
        const message = typeof errData.detail === 'string' ? errData.detail : 'Registration failed. Please check your details.';
        throw new Error(message);
      }
      return await res.json();
    } catch (err: unknown) {
      throw parseFetchError(err, 'Registration failed. Please try again.');
    }
  },

  async login(data: LoginPayload): Promise<AuthResponse> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Invalid email/mobile or password' }));
        const message = typeof errData.detail === 'string' ? errData.detail : 'Invalid credentials. Please try again.';
        throw new Error(message);
      }
      return await res.json();
    } catch (err: unknown) {
      throw parseFetchError(err, 'Login failed. Please check your credentials and internet connection.');
    }
  },

  async getMe(token: string) {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Session expired or unauthorized.');
      return await res.json();
    } catch (err: unknown) {
      throw parseFetchError(err, 'Unable to retrieve user profile.');
    }
  }
};

