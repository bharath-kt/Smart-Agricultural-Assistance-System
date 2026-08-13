import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  timestamp: string;
}

export const Chatbot: React.FC = () => {
  const { language, t } = useLanguage();
  const { profile, isAuthenticated } = useAuth();

  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'bot',
      text: t('chat.welcomeMsg'),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].id === 'welcome') {
        return [
          {
            id: 'welcome',
            sender: 'bot',
            text: isAuthenticated && profile?.full_name
              ? (language === 'kn'
                ? `ನಮಸ್ಕಾರ ${profile.full_name}! ನಾನು ನಿಮ್ಮ ಅಗ್ರೋ ಪಲ್ಸ್ ಸಹಾಯಕ. ನಿಮ್ಮ ಕೃಷಿ ವಿವರಗಳು (${profile.district || 'ಮೈಸೂರು'}, ${profile.farmer_category || 'ಸಣ್ಣ'} ರೈತರು, ಬೆಳೆಗಳು: ${profile.crops_grown?.join(', ') || 'ಟೊಮೆಟೊ'}) ಆಧಾರದ ಮೇಲೆ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಿದ್ದೇನೆ.`
                : `Hello ${profile.full_name}! I am your AgroPulse Assistant. Based on your saved profile (${profile.district || 'Mysuru'}, ${profile.farmer_category || 'Small'} Farmer, Crops: ${profile.crops_grown?.join(', ') || 'Tomato'}), how can I assist your farm today?`)
              : t('chat.welcomeMsg'),
            timestamp: prev[0].timestamp,
          },
        ];
      }
      return prev;
    });
  }, [language, t, isAuthenticated, profile]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const getBotResponse = (query: string, lang: 'en' | 'kn'): string => {
    const q = query.toLowerCase();

    const farmerName = profile?.full_name || 'Farmer';
    const farmerDistrict = profile?.district || 'Mysuru';
    const farmerState = profile?.state || 'Karnataka';
    const farmerCrops = profile?.crops_grown?.join(', ') || 'Tomato, Paddy';
    const farmerCategory = profile?.farmer_category || 'Small';

    if (lang === 'kn') {
      if (q.includes('ಹವಾಮಾನ') || q.includes('ಮಳೆ') || q.includes(' weather') || q.includes('rain')) {
        return `ನಿಮ್ಮ ಉಳಿಸಿದ ಸ್ಥಳವಾದ ${farmerDistrict}, ${farmerState} ನಲ್ಲಿ ಪ್ರಸ್ತುತ ಹವಾಮಾನವು ಬೆಳೆ ಬೆಳೆಯಲು ಅನುಕೂಲಕರವಾಗಿದೆ. ನಮ್ಮ "ಹವಾಮಾನ" ವಿಭಾಗದಲ್ಲಿ 5 ದಿನಗಳ ವಿವರವಾದ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆಯನ್ನು ಪಡೆಯಬಹುದು.`;
      }
      if (q.includes('ಬೆಲೆ') || q.includes('ಮಾರುಕಟ್ಟೆ') || q.includes(' market') || q.includes('price')) {
        return `ನಿಮ್ಮ ಬೆಳೆಗಳಾದ (${farmerCrops}) ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು ಪ್ರಸ್ತುತ ಸ್ಥಿರತೆಯಿಂದ ಏರಿಕೆಯತ್ತ ಸಾಗುತ್ತಿವೆ. ನಮ್ಮ "ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು" ಪುಟದಲ್ಲಿ 7-ದಿನಗಳ ಮುನ್ಸೂಚನೆಯನ್ನು ವೀಕ್ಷಿಸಿ.`;
      }
      if (q.includes('ಯೋಜನೆ') || q.includes('ಸರ್ಕಾರ') || q.includes(' scheme') || q.includes(' subsidy') || q.includes('ಸಹಾಯಧನ')) {
        return `ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ಪ್ರಕಾರ (${farmerState} ರಾಜ್ಯ, ${farmerCategory} ರೈತರು, ಭೂಮಿ: ${profile?.land_size || 1.5} Ha), ನೀವು ಪಿಎಂ-ಕಿಸಾನ್, ಪಿಎಂಎಫ್‌ಬಿವೈ, ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (KCC), ಮತ್ತು ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆಗೆ ಅರ್ಹರಾಗಿದ್ದೀರಿ. ನಮ್ಮ "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು" ಪುಟದಲ್ಲಿ ನಿಮ್ಮ ಅರ್ಹತೆ ಪರಿಶೀಲಿಸಿ.`;
      }
      if (q.includes('ರೋಗ') || q.includes('ಎಲೆ') || q.includes(' disease') || q.includes(' crop')) {
        return `ನಿಮ್ಮ ಬೆಳೆಗಳಾದ ${farmerCrops} ಎಲೆಯ ಫೋಟೋವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡುವ ಮೂಲಕ AI ಬೆಳೆ ರೋಗ ಪತ್ತೆ ಸೌಲಭ್ಯವನ್ನು ಬಳಸಿ. "ರೋಗ ಪತ್ತೆ" ವಿಭಾಗದಲ್ಲಿ ಚಿಕಿತ್ಸೆ ಮತ್ತು ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳನ್ನು ಪಡೆಯಿರಿ.`;
      }
      if (q.includes('ನಮಸ್ಕಾರ') || q.includes('ಹಲೋ') || q.includes('hi') || q.includes('hello')) {
        return `ನಮಸ್ಕಾರ ${farmerName}! ನಾನು ನಿಮ್ಮ ಅಗ್ರೋ ಪಲ್ಸ್ ಕೃಷಿ ಸಹಾಯಕ. ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?`;
      }
      return `ಧನ್ಯವಾದಗಳು ${farmerName}! ನಿಮ್ಮ ${farmerDistrict} ಜಮೀನಿನ ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಕೃಷಿ ರೋಗಗಳು ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಮಾಹಿತಿ ಪಡೆಯಲು ಅಗ್ರೋ ಪಲ್ಸ್ ಅಪ್ಲಿಕೇಶನ್ ಬಳಸಬಹುದು.`;
    } else {
      if (q.includes('weather') || q.includes('rain') || q.includes('temp')) {
        return `Current weather conditions in your location (${farmerDistrict}, ${farmerState}) are favorable for your crops (${farmerCrops}). You can view the 5-day detailed forecast in the Weather tab.`;
      }
      if (q.includes('market') || q.includes('price') || q.includes('rate')) {
        return `Market prices for your saved crops (${farmerCrops}) are showing upward momentum in ${farmerDistrict} mandi. Check the Market Prices tab for complete 7-day analytics.`;
      }
      if (q.includes('scheme') || q.includes('subsidy') || q.includes('loan') || q.includes('pm-kisan')) {
        return `Based on your saved profile as a ${farmerCategory} farmer in ${farmerState} with ${profile?.land_size || 1.5} Ha, you match PM-KISAN (Rs 6,000/yr), PMFBY Crop Insurance, Kisan Credit Card (4% interest), and Krishi Bhagya schemes! Visit the Government Schemes section to see detailed eligibility rules and apply.`;
      }
      if (q.includes('disease') || q.includes('leaf') || q.includes('spot') || q.includes('blight')) {
        return `You can upload a leaf photo of your crops (${farmerCrops}) in our Disease Detection module to get immediate AI diagnosis and treatment recommendations.`;
      }
      if (q.includes('hello') || q.includes('hi') || q.includes('hey')) {
        return `Hello ${farmerName}! I am your AgroPulse Assistant. How can I assist your farming operations in ${farmerDistrict} today?`;
      }
      return `Thank you for reaching out, ${farmerName}! Feel free to ask about weather updates in ${farmerDistrict}, market prices for ${farmerCrops}, or eligible government schemes.`;
    }
  };

  const handleSend = (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInput('');

    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: getBotResponse(text, language),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botResponse]);
    }, 500);
  };

  const quickQueries = [
    t('chat.quickQueries.weather'),
    t('chat.quickQueries.market'),
    t('chat.quickQueries.schemes'),
    t('chat.quickQueries.disease'),
  ];

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 flex items-center gap-2 group border border-white/20"
        aria-label={t('chat.openBtn')}
      >
        <div className="relative">
          <MessageSquare className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 border-2 border-primary-600 rounded-full animate-ping"></span>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 border-2 border-primary-600 rounded-full"></span>
        </div>
        <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 ease-in-out whitespace-nowrap text-sm font-semibold pr-1">
          {t('chat.openBtn')}
        </span>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 md:right-6 z-50 w-[calc(100vw-2rem)] md:w-96 h-[520px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-slideUp">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-4 text-white flex items-center justify-between shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/30">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                  <span>{t('chat.botName')}</span>
                  <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                </h3>
                <p className="text-[11px] text-primary-100">{t('chat.botStatus')}</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors text-white"
              aria-label={t('chat.closeBtn')}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-gray-50/50">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-7 h-7 bg-primary-600 rounded-lg flex items-center justify-center shrink-0 text-white mt-1 shadow-xs">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-primary-600 text-white rounded-br-none shadow-sm'
                      : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none shadow-xs'
                  }`}
                >
                  <p>{msg.text}</p>
                  <span
                    className={`block text-[9px] mt-1 text-right ${
                      msg.sender === 'user' ? 'text-primary-200' : 'text-gray-400'
                    }`}
                  >
                    {msg.timestamp}
                  </span>
                </div>

                {msg.sender === 'user' && (
                  <div className="w-7 h-7 bg-gray-200 rounded-lg flex items-center justify-center shrink-0 text-gray-700 mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Query Pills */}
          <div className="px-3 py-2 bg-white border-t border-gray-100 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {quickQueries.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                className="px-2.5 py-1 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-lg text-[11px] font-semibold whitespace-nowrap transition-colors border border-primary-100"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-white border-t border-gray-200 flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t('chat.placeholder')}
              className="flex-1 px-3 py-2 text-xs border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="p-2.5 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-xl transition-all shadow-xs shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
