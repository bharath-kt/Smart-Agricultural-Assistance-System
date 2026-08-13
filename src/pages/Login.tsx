import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sprout, LogIn, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

export default function Login() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim() || !password) {
      setError(language === 'kn' ? 'ದಯವಿಟ್ಟು ಮೊಬೈಲ್/ಇಮೇಲ್ ಮತ್ತು ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ' : 'Please enter your email/mobile and password.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await login(identifier, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || (language === 'kn' ? 'ಲಾಗಿನ್ ವಿಫಲವಾಗಿದೆ. ಪರಿಶೀಲಿಸಿ.' : 'Login failed. Please check credentials.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-10 px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-gray-100 p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-14 h-14 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto shadow-md shadow-primary-200">
            <Sprout className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            {language === 'kn' ? 'ರೈತರ ಲಾಗಿನ್' : 'Farmer Login'}
          </h2>
          <p className="text-sm text-gray-500">
            {language === 'kn'
              ? 'ನಿಮ್ಮ ಕೃಷಿ ಖಾತೆಗೆ ಲಾಗಿನ್ ಮಾಡಿ ಮತ್ತು ಸೇವೆಗಳನ್ನು ಪಡೆದುಕೊಳ್ಳಿ'
              : 'Sign in to access personalized agricultural assistance & schemes'}
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl flex items-center gap-3 text-sm animate-shake">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              {language === 'kn' ? 'ಇಮೇಲ್ ಅಥವಾ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ' : 'Email or Mobile Number'}
            </label>
            <input
              type="text"
              required
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder={language === 'kn' ? 'ಉದಾ: farmer@gmail.com ಅಥವಾ 9876543210' : 'e.g. farmer@gmail.com or 9876543210'}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              {language === 'kn' ? 'ಪಾಸ್‌ವರ್ಡ್ (Password)' : 'Password'}
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl shadow-lg shadow-primary-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <span>{language === 'kn' ? 'ಲಾಗಿನ್ ಆಗುತ್ತಿದೆ...' : 'Signing in...'}</span>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                <span>{language === 'kn' ? 'ಲಾಗಿನ್ ಮಾಡಿ' : 'Login to Dashboard'}</span>
              </>
            )}
          </button>
        </form>

        <div className="border-t border-gray-100 pt-6 text-center space-y-3">
          <p className="text-sm text-gray-600">
            {language === 'kn' ? 'ಖಾತೆ ಇಲ್ಲವೇ?' : "Don't have a farmer account yet?"}{' '}
            <Link to="/signup" className="text-primary-600 hover:underline font-semibold inline-flex items-center gap-1">
              <span>{language === 'kn' ? 'ಇಲ್ಲಿ ಸೈನ್ ಅಪ್ ಮಾಡಿ' : 'Sign Up Free'}</span>
              <ArrowRight className="w-4 h-4" />
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
