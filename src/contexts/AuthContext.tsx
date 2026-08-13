import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi, type AuthResponse, type SignupPayload } from '../services/authApi';
import { profileApi, type FarmerProfileData } from '../services/profileApi';

interface AuthContextType {
  token: string | null;
  user: { id: number; full_name?: string; email?: string; mobile_number?: string } | null;
  profile: FarmerProfileData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (identifier: string, pass: string) => Promise<void>;
  signup: (data: SignupPayload) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<FarmerProfileData>) => Promise<FarmerProfileData>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('smart_agri_token'));
  const [user, setUser] = useState<{ id: number; full_name?: string; email?: string; mobile_number?: string } | null>(null);
  const [profile, setProfile] = useState<FarmerProfileData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchUserData = async (jwtToken: string) => {
    try {
      const userData = await authApi.getMe(jwtToken);
      setUser({
        id: userData.id,
        full_name: userData.full_name,
        email: userData.email,
        mobile_number: userData.mobile_number
      });
      if (userData.profile) {
        setProfile(userData.profile);
      } else {
        const prof = await profileApi.getProfile(jwtToken);
        setProfile(prof);
      }
    } catch (err) {
      console.error('Failed to load user auth state:', err);
      // Clear token if invalid
      localStorage.removeItem('smart_agri_token');
      setToken(null);
      setUser(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchUserData(token);
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = async (identifier: string, pass: string) => {
    setIsLoading(true);
    setUser(null);
    setProfile(null);
    try {
      const res: AuthResponse = await authApi.login({ identifier, password: pass });
      localStorage.setItem('smart_agri_token', res.access_token);
      setToken(res.access_token);
      await fetchUserData(res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: SignupPayload) => {
    setIsLoading(true);
    setUser(null);
    setProfile(null);
    try {
      const res: AuthResponse = await authApi.signup(data);
      localStorage.setItem('smart_agri_token', res.access_token);
      setToken(res.access_token);
      await fetchUserData(res.access_token);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('smart_agri_token');
    setToken(null);
    setUser(null);
    setProfile(null);
  };

  const updateProfile = async (data: Partial<FarmerProfileData>) => {
    if (!token) throw new Error('Not authenticated');
    const updated = await profileApi.updateProfile(token, data);
    setProfile(updated);
    if (updated.full_name) {
      setUser(prev => prev ? { ...prev, full_name: updated.full_name } : null);
    }
    return updated;
  };

  const refreshProfile = async () => {
    if (token) await fetchUserData(token);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        profile,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        signup,
        logout,
        updateProfile,
        refreshProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
