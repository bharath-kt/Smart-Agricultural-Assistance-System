import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { User, MapPin, Sprout, Save, AlertCircle, CheckCircle2, ShieldCheck } from 'lucide-react';

const ALL_CROPS = ['Tomato', 'Corn', 'Paddy', 'Wheat', 'Sugarcane', 'Cotton', 'Chilli', 'Onion', 'Potato', 'Groundnut', 'Banana', 'Turmeric'];

export default function Profile() {
  const { profile, updateProfile, isAuthenticated } = useAuth();
  const { language } = useLanguage();

  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState<number | ''>(35);
  const [gender, setGender] = useState('Male');
  const [state, setState] = useState('Karnataka');
  const [district, setDistrict] = useState('Mysuru');
  const [farmerCategory, setFarmerCategory] = useState('Small');
  const [landOwnership, setLandOwnership] = useState('Owned');
  const [landSize, setLandSize] = useState<number | ''>(1.5);
  const [cropsGrown, setCropsGrown] = useState<string[]>(['Tomato', 'Paddy']);
  const [annualIncome, setAnnualIncome] = useState<number | ''>(180000);
  const [irrigationType, setIrrigationType] = useState('Well');
  const [farmingType, setFarmingType] = useState('Conventional');

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (profile) {
      if (profile.full_name) setFullName(profile.full_name);
      if (profile.age) setAge(profile.age);
      if (profile.gender) setGender(profile.gender);
      if (profile.state) setState(profile.state);
      if (profile.district) setDistrict(profile.district);
      if (profile.farmer_category) setFarmerCategory(profile.farmer_category);
      if (profile.land_ownership) setLandOwnership(profile.land_ownership);
      if (profile.land_size) setLandSize(profile.land_size);
      if (profile.crops_grown) setCropsGrown(profile.crops_grown);
      if (profile.annual_income) setAnnualIncome(profile.annual_income);
      if (profile.irrigation_type) setIrrigationType(profile.irrigation_type);
      if (profile.farming_type) setFarmingType(profile.farming_type);
    }
  }, [profile]);

  const toggleCrop = (crop: string) => {
    setCropsGrown(prev =>
      prev.includes(crop) ? prev.filter(c => c !== crop) : [...prev, crop]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setSaving(true);

    try {
      await updateProfile({
        full_name: fullName,
        age: typeof age === 'number' ? age : 35,
        gender,
        state,
        district,
        farmer_category: farmerCategory,
        land_ownership: landOwnership,
        land_size: typeof landSize === 'number' ? landSize : 1.5,
        crops_grown: cropsGrown,
        annual_income: typeof annualIncome === 'number' ? annualIncome : 180000,
        irrigation_type: irrigationType,
        farming_type: farmingType
      });
      setMessage({
        type: 'success',
        text: language === 'kn' ? 'ನಿಮ್ಮ ರೈತರ ಪ್ರೊಫೈಲ್ ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ!' : 'Farmer profile updated successfully!'
      });
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.message || (language === 'kn' ? 'ಪ್ರೊಫೈಲ್ ಉಳಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ' : 'Failed to update profile.')
      });
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl shadow-lg text-center space-y-4">
        <User className="w-12 h-12 text-primary-600 mx-auto" />
        <h3 className="text-xl font-bold text-gray-900">
          {language === 'kn' ? 'ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ' : 'Authentication Required'}
        </h3>
        <p className="text-sm text-gray-500">
          {language === 'kn' ? 'ಪ್ರೊಫೈಲ್ ವೀಕ್ಷಿಸಲು ಮತ್ತು ಮಾರ್ಪಡಿಸಲು ಲಾಗಿನ್ ಆಗಿ.' : 'Please sign in to view and edit your farmer profile.'}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-primary-700 via-primary-600 to-green-700 rounded-2xl p-6 lg:p-8 text-white shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-primary-200 text-xs uppercase font-bold tracking-wider">
            <ShieldCheck className="w-4 h-4 text-green-300" />
            <span>{language === 'kn' ? 'ರೈತರ ವಿವರಗಳು' : 'Farmer Credentials'}</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold">
            {fullName || 'Farmer Profile'}
          </h1>
          <p className="text-sm text-primary-100 flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            <span>{district}, {state}</span> • <span>{farmerCategory} Farmer</span>
          </p>
        </div>
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl px-4 py-2 text-xs font-semibold">
          Saved Details Pre-fill Engine Active
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-xl flex items-center gap-3 text-sm font-medium ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <AlertCircle className="w-5 h-5 shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 lg:p-8 space-y-8">
        {/* Personal & Demographic Info */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-100 pb-3">
            <User className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-bold text-gray-900">
              {language === 'kn' ? '1. ವೈಯಕ್ತಿಕ ವಿವರಗಳು (Personal Information)' : '1. Personal Information'}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ಪೂರ್ಣ ಹೆಸರು' : 'Full Name'}
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ವಯಸ್ಸು (Age)' : 'Age (Years)'}
              </label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value ? parseInt(e.target.value) : '')}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ಲಿಂಗ (Gender)' : 'Gender'}
              </label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none bg-white"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        {/* Location & Land Info */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-100 pb-3">
            <MapPin className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-bold text-gray-900">
              {language === 'kn' ? '2. ಸ್ಥಳ ಮತ್ತು ಭೂಮಿ ವಿವರಗಳು (Location & Land Details)' : '2. Location & Land Holding'}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ರಾಜ್ಯ (State)' : 'State'}
              </label>
              <input
                type="text"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ಜಿಲ್ಲೆ (District)' : 'District'}
              </label>
              <input
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ರೈತರ ವರ್ಗ' : 'Farmer Category'}
              </label>
              <select
                value={farmerCategory}
                onChange={(e) => setFarmerCategory(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none bg-white"
              >
                <option value="Small">Small (&lt; 2 Ha)</option>
                <option value="Marginal">Marginal (&lt; 1 Ha)</option>
                <option value="Medium">Medium (2-5 Ha)</option>
                <option value="Large">Large (&gt; 5 Ha)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ಭೂಮಿ ವಿಸ್ತೀರ್ಣ (ಹೆಕ್ಟೇರ್)' : 'Land Size (Hectares)'}
              </label>
              <input
                type="number"
                step="0.1"
                value={landSize}
                onChange={(e) => setLandSize(e.target.value ? parseFloat(e.target.value) : '')}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ಭೂ ಮಾಲೀಕತ್ವ (Land Ownership)' : 'Land Ownership Type'}
              </label>
              <select
                value={landOwnership}
                onChange={(e) => setLandOwnership(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none bg-white"
              >
                <option value="Owned">Owned (ಸ್ವಂತ ಭೂಮಿ)</option>
                <option value="Leased">Leased / Tenant (ಗುತ್ತಿಗೆ ಭೂಮಿ)</option>
                <option value="Joint">Joint Family Land (ಜಂಟಿ ಭೂಮಿ)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ವಾರ್ಷಿಕ ಆದಾಯ (Annual Income Rs.)' : 'Annual Income (Rs.)'}
              </label>
              <input
                type="number"
                value={annualIncome}
                onChange={(e) => setAnnualIncome(e.target.value ? parseFloat(e.target.value) : '')}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
          </div>
        </div>

        {/* Crops & Farming Practices */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-100 pb-3">
            <Sprout className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-bold text-gray-900">
              {language === 'kn' ? '3. ಬೆಳೆಗಳು ಮತ್ತು ಕೃಷಿ ಪದ್ಧತಿ (Crops & Farming Practices)' : '3. Crops & Farming Practices'}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ನೀರುಣಿಸುವಿಕೆ (Irrigation Availability)' : 'Irrigation Type'}
              </label>
              <select
                value={irrigationType}
                onChange={(e) => setIrrigationType(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none bg-white"
              >
                <option value="Well">Borewell / Open Well (ಬೋರ್‌ವೆಲ್/ಬಾವಿ)</option>
                <option value="Rainfed">Rainfed / Dryland (ಮಳೆ ಆಶ್ರಿತ)</option>
                <option value="Canal">Canal Irrigation (ಕಾಲುವೆ ನೀರು)</option>
                <option value="Drip/Sprinkler">Drip / Sprinkler Micro-irrigation (ಹನಿ ನೀರಾವರಿ)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">
                {language === 'kn' ? 'ಕೃಷಿ ಮಾದರಿ (Farming Type)' : 'Farming Type'}
              </label>
              <select
                value={farmingType}
                onChange={(e) => setFarmingType(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none bg-white"
              >
                <option value="Conventional">Conventional Farming (ಸಾಂಪ್ರದಾಯಿಕ ಕೃಷಿ)</option>
                <option value="Organic">Organic Farming (ಸಾವಯವ ಕೃಷಿ)</option>
                <option value="Mixed">Mixed / Integrated Farming (ಸಂಯೋಜಿತ ಕೃಷಿ)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase mb-2">
              {language === 'kn' ? 'ಬೆಳೆಯುವ ಬೆಳೆಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ (Select Crops Grown)' : 'Select Crops Grown'}
            </label>
            <div className="flex flex-wrap gap-2">
              {ALL_CROPS.map((crop) => {
                const active = cropsGrown.includes(crop);
                return (
                  <button
                    key={crop}
                    type="button"
                    onClick={() => toggleCrop(crop)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                      active
                        ? 'bg-primary-600 text-white shadow-sm'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {active && <CheckCircle2 className="w-3.5 h-3.5" />}
                    <span>{crop}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-100 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-200 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            <span>{saving ? 'Saving...' : (language === 'kn' ? 'ಪ್ರೊಫೈಲ್ ಉಳಿಸಿ' : 'Save Farmer Profile')}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
