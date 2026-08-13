import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations, type Language } from '../i18n/translations';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  hasSelectedLanguage: boolean;
  completeFirstLaunch: (lang: Language) => void;
  t: (key: string, defaultText?: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_KEY = 'app_language';
const FIRST_LAUNCH_KEY = 'has_selected_language';

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const savedLang = localStorage.getItem(LANGUAGE_KEY);
    return (savedLang === 'kn' || savedLang === 'en') ? savedLang : 'en';
  });

  const [hasSelectedLanguage, setHasSelectedLanguage] = useState<boolean>(() => {
    return localStorage.getItem(FIRST_LAUNCH_KEY) === 'true';
  });

  useEffect(() => {
    localStorage.setItem(LANGUAGE_KEY, language);
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem(LANGUAGE_KEY, lang);
  };

  const completeFirstLaunch = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem(LANGUAGE_KEY, lang);
    localStorage.setItem(FIRST_LAUNCH_KEY, 'true');
    setHasSelectedLanguage(true);
  };

  const t = (key: string, defaultText?: string): string => {
    const keys = key.split('.');
    let value: any = translations[language];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Fallback to English if missing in selected language
        let fallbackValue: any = translations['en'];
        for (const fk of keys) {
          if (fallbackValue && typeof fallbackValue === 'object' && fk in fallbackValue) {
            fallbackValue = fallbackValue[fk];
          } else {
            return defaultText || key;
          }
        }
        return typeof fallbackValue === 'string' ? fallbackValue : defaultText || key;
      }
    }

    return typeof value === 'string' ? value : defaultText || key;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        hasSelectedLanguage,
        completeFirstLaunch,
        t,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
