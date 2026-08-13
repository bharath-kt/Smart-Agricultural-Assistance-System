import React, { useState } from 'react';
import { Sprout, Check, Globe } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import type { Language } from '../i18n/translations';

interface LanguageSelectionModalProps {
  onComplete: () => void;
}

export const LanguageSelectionModal: React.FC<LanguageSelectionModalProps> = ({ onComplete }) => {
  const { completeFirstLaunch } = useLanguage();
  const [selected, setSelected] = useState<Language>('en');

  const handleConfirm = () => {
    completeFirstLaunch(selected);
    onComplete();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-gray-100 transform transition-all duration-300 scale-100">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-500 p-8 text-white text-center relative overflow-hidden">
          <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-white/10 rounded-full blur-xl pointer-events-none"></div>
          <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center mx-auto mb-4 border border-white/30 shadow-inner">
            <Sprout className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight">AgroPulse</h1>
          <p className="text-primary-100 mt-1 font-medium text-base">Smart Farming Assistance System</p>
          <p className="text-white/90 text-sm mt-3 font-semibold bg-white/10 inline-block px-4 py-1.5 rounded-full border border-white/20">
            ಅಗ್ರೋ ಪಲ್ಸ್ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯ ವ್ಯವಸ್ಥೆ
          </p>
        </div>

        {/* Content */}
        <div className="p-6 md:p-8 space-y-6">
          <div className="text-center space-y-1">
            <div className="flex items-center justify-center gap-2 text-primary-600 mb-1">
              <Globe className="w-5 h-5" />
              <span className="font-semibold text-sm uppercase tracking-wider">Select Language / ಭಾಷೆ ಆಯ್ಕೆ</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900">Choose Your Preferred Language</h2>
            <p className="text-sm text-gray-500">ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ</p>
          </div>

          {/* Options */}
          <div className="grid grid-cols-1 gap-4">
            {/* English Option */}
            <button
              type="button"
              onClick={() => setSelected('en')}
              className={`flex items-center justify-between p-5 rounded-xl border-2 transition-all duration-200 text-left ${
                selected === 'en'
                  ? 'border-primary-500 bg-primary-50/80 shadow-md ring-2 ring-primary-500/20'
                  : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
                  selected === 'en' ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-700'
                }`}>
                  EN
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-lg">English</h3>
                  <p className="text-xs text-gray-500">Continue application in English</p>
                </div>
              </div>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${
                selected === 'en' ? 'bg-primary-500 text-white' : 'border border-gray-300'
              }`}>
                {selected === 'en' && <Check className="w-4 h-4" />}
              </div>
            </button>

            {/* Kannada Option */}
            <button
              type="button"
              onClick={() => setSelected('kn')}
              className={`flex items-center justify-between p-5 rounded-xl border-2 transition-all duration-200 text-left ${
                selected === 'kn'
                  ? 'border-primary-500 bg-primary-50/80 shadow-md ring-2 ring-primary-500/20'
                  : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
                  selected === 'kn' ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-700'
                }`}>
                  ಕ
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 text-lg">ಕನ್ನಡ (Kannada)</h3>
                  <p className="text-xs text-gray-500">ಅಪ್ಲಿಕೇಶನ್ ಅನ್ನು ಕನ್ನಡದಲ್ಲಿ ಬಳಸಿ</p>
                </div>
              </div>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${
                selected === 'kn' ? 'bg-primary-500 text-white' : 'border border-gray-300'
              }`}>
                {selected === 'kn' && <Check className="w-4 h-4" />}
              </div>
            </button>
          </div>

          {/* Action */}
          <button
            type="button"
            onClick={handleConfirm}
            className="w-full btn-primary py-3.5 text-base font-bold rounded-xl shadow-lg hover:shadow-primary-500/30 transition-all flex items-center justify-center gap-2"
          >
            <span>Continue / ಮುಂದುವರಿಸಿ</span>
          </button>
        </div>
      </div>
    </div>
  );
};
