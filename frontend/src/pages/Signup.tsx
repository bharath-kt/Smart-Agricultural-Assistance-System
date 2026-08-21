import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sprout, UserPlus, AlertCircle, Check, ShieldCheck } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

const AVAILABLE_CROPS = ['Tomato', 'Corn', 'Paddy', 'Wheat', 'Sugarcane', 'Cotton', 'Chilli', 'Onion', 'Potato', 'Groundnut'];

export default function Signup() {
  const [fullName, setFullName] = useState('');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [state, setState] = useState('Karnataka');
  const [district, setDistrict] = useState('Mysuru');
  const [farmerCategory, setFarmerCategory] = useState('Small');
  const [landSize, setLandSize] = useState('1.5');
  const [selectedCrops, setSelectedCrops] = useState<string[]>(['Tomato', 'Paddy']);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signup } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();

  const toggleCrop = (crop: string) => {
    setSelectedCrops(prev =>
      prev.includes(crop) ? prev.filter(c => c !== crop) : [...prev, crop]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !identifier.trim() || !password) {
      setError(language === 'kn' ? 'ದಯವಿಟ್ಟು ಎಲ್ಲಾ ಕಡ್ಡಾಯ ಕ್ಷೇತ್ರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ' : 'Please fill in all required fields.');
      return;
    }

    if (password.length < 6) {
      setError(language === 'kn' ? 'ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳನ್ನು ಹೊಂದಿರಬೇಕು' : 'Password must be at least 6 characters long.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await signup({
        full_name: fullName.trim(),
        identifier: identifier.trim(),
        password,
        state,
        district,
        farmer_category: farmerCategory,
        land_size: parseFloat(landSize) || 1.5,
        crops_grown: selectedCrops.length > 0 ? selectedCrops : ['Tomato', 'Paddy']
      });
      navigate('/');
    } catch (err: any) {
      setError(err.message || (language === 'kn' ? 'ಖಾತೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ.' : 'Signup failed. User may already exist.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-10 px-4">
      <div className="max-w-xl w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto shadow-md shadow-primary-200">
            <Sprout className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            {language === 'kn' ? 'ಅಗ್ರಿಮಿತ್ರ AI – ರೈತರ ನೋಂದಣಿ' : 'AgriMitra AI – Farmer Registration'}
          </h2>
          <p className="text-sm text-gray-500">
            {language === 'kn'
              ? 'ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಬೆಳೆ ನೆರವು ಪಡೆಯಲು ನಿಮ್ಮ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ'
              : 'Create your account to unlock government scheme recommendations & personalization'}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-3 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                {language === 'kn' ? 'ಪೂರ್ಣ ಹೆಸರು *' : 'Full Name *'}
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder={language === 'kn' ? 'ನಿಮ್ಮ ಹೆಸರು' : 'e.g. Ramesh Kumar'}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                {language === 'kn' ? 'ಇಮೇಲ್ ಅಥವಾ ಮೊಬೈಲ್ *' : 'Email or Mobile *'}
              </label>
              <input
                type="text"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={language === 'kn' ? 'ಇಮೇಲ್/ಮೊಬೈಲ್' : 'e.g. 9876543210'}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                {language === 'kn' ? 'ಪಾಸ್‌ವರ್ಡ್ *' : 'Password *'}
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 6 characters"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
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
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                {language === 'kn' ? 'ರಾಜ್ಯ' : 'State'}
              </label>
              <input
                type="text"
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                {language === 'kn' ? 'ಜಿಲ್ಲೆ' : 'District'}
              </label>
              <input
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                {language === 'kn' ? 'ಭೂಮಿ (ಹೆಕ್ಟೇರ್)' : 'Land Size (Hectares)'}
              </label>
              <input
                type="number"
                step="0.1"
                value={landSize}
                onChange={(e) => setLandSize(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
              {language === 'kn' ? 'ಬೆಳೆಯುವ ಬೆಳೆಗಳು (Crops Grown)' : 'Crops Grown'}
            </label>
            <div className="flex flex-wrap gap-2">
              {AVAILABLE_CROPS.map((crop) => {
                const isSelected = selectedCrops.includes(crop);
                return (
                  <button
                    key={crop}
                    type="button"
                    onClick={() => toggleCrop(crop)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                      isSelected
                        ? 'bg-primary-600 text-white shadow-sm'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {isSelected && <Check className="w-3.5 h-3.5" />}
                    <span>{crop}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50 mt-4"
          >
            {loading ? (
              <span>{language === 'kn' ? 'ನೋಂದಾಯಿಸಲಾಗುತ್ತಿದೆ...' : 'Creating Farmer Profile...'}</span>
            ) : (
              <>
                <UserPlus className="w-5 h-5" />
                <span>{language === 'kn' ? 'ಉಚಿತವಾಗಿ ನೋಂದಾಯಿಸಿ' : 'Register Farmer Account'}</span>
              </>
            )}
          </button>
        </form>

        <div className="border-t border-gray-100 pt-4 text-center space-y-2">
          <p className="text-sm text-gray-600">
            {language === 'kn' ? 'ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?' : 'Already registered?'}{' '}
            <Link to="/login" className="text-primary-600 hover:underline font-semibold">
              {language === 'kn' ? 'ಇಲ್ಲಿ ಲಾಗಿನ್ ಮಾಡಿ' : 'Log In Here'}
            </Link>
          </p>
          <div className="flex items-center justify-center gap-1.5 text-xs text-gray-400">
            <ShieldCheck className="w-4 h-4 text-green-500" />
            <span>Secure Password Encryption & Authenticated Data</span>
          </div>
        </div>
      </div>
    </div>
  );
}
