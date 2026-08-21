import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  X,
  Send,
  Bot,
  User,
  Sparkles,
  Loader2,
  Trash2,
  RotateCcw,
  CloudSun,
  Sprout,
  Bug,
  BadgeIndianRupee,
  Landmark
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { sendChatMessage } from '../services/chatApi';
import type { ChatMessagePayload } from '../services/chatApi';

interface Message {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  timestamp: string;
}

export const Chatbot: React.FC = () => {
  const { language, t } = useLanguage();
  const { profile, token, isAuthenticated } = useAuth();

  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeText =
        isAuthenticated && profile?.full_name
          ? language === 'kn'
            ? `ನಮಸ್ಕಾರ ${profile.full_name}! ನಾನು ನಿಮ್ಮ ಅಗ್ರಿಮಿತ್ರ AI ಸಹಾಯಕ. ${profile.district || 'ಮೈಸೂರು'} ಪ್ರದೇಶದ ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ಬೆಳೆ ಸಲಹೆ ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಿದ್ದೇನೆ.`
            : `Hello ${profile.full_name}! I am your AgriMitra AI Assistant. How can I assist your farming in ${profile.district || 'Mysuru'} today?`
          : t('chat.welcomeMsg') ||
            (language === 'kn'
              ? 'ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಕೃಷಿ AI ಸಹಾಯಕ. ಹವಾಮಾನ, ಬೆಳೆ ಬೆಲೆಗಳು, ಸಸ್ಯ ರೋಗಗಳು ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಕುರಿತು ಕೇಳಿ.'
              : 'Hello! I am your AI Agriculture Assistant. Ask me about weather, market prices, crop diseases, or government schemes.');

      setMessages([
        {
          id: 'welcome',
          sender: 'bot',
          text: welcomeText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  }, [language, t, isAuthenticated, profile, messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, loading, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const messageText = (textToSend || input).trim();
    if (!messageText || loading) return;

    setError(null);
    const userMsgId = Date.now().toString();
    const userMessage: Message = {
      id: userMsgId,
      sender: 'user',
      text: messageText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    if (!textToSend) setInput('');
    setLoading(true);

    // Prepare history payload for multi-turn context memory
    const historyPayload: ChatMessagePayload[] = updatedMessages
      .filter((m) => m.id !== 'welcome')
      .slice(-6)
      .map((m) => ({
        sender: m.sender,
        text: m.text
      }));

    try {
      const res = await sendChatMessage(messageText, language, historyPayload, token || undefined);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err: unknown) {
      console.error('Chatbot API error:', err);
      const errDetail =
        err instanceof Error
          ? err.message
          : language === 'kn'
          ? 'ಸೇವೆಯಲ್ಲಿ ಸಣ್ಣ ಅಡಚಣೆ ಉಂಟಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.'
          : 'Unable to connect to assistant service. Please try again.';

      setError(errDetail);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError(null);
  };

  const quickActions = [
    {
      icon: CloudSun,
      label: language === 'kn' ? '🌦️ ಹವಾಮಾನ' : '🌦️ Weather',
      query: language === 'kn' ? 'ಇಂದು ಹವಾಮಾನ ಮತ್ತು ಮಳೆ ಮುನ್ಸೂಚನೆ ಏನು?' : 'What is today weather forecast and rainfall outlook?'
    },
    {
      icon: Sprout,
      label: language === 'kn' ? '🌱 ಬೆಳೆ ಸಲಹೆ' : '🌱 Crop Advice',
      query: language === 'kn' ? 'ಟೊಮೆಟೊ ಬೆಳೆಗೆ ಯಾವ ರಸಗೊಬ್ಬರ ಮತ್ತು ನೀರಾವರಿ ಉತ್ತಮ?' : 'What fertilizer and irrigation is recommended for Tomato?'
    },
    {
      icon: Bug,
      label: language === 'kn' ? '🦠 ರೋಗ ನೆರವು' : '🦠 Disease Help',
      query: language === 'kn' ? 'ಟೊಮೆಟೊ ಎಲೆಗಳಲ್ಲಿ ಕಪ್ಪು ಕಲೆಗಳು ಬಂದರೆ ಏನು ಮಾಡಬೇಕು?' : 'What disease causes dark spots on tomato leaves and how to treat it?'
    },
    {
      icon: BadgeIndianRupee,
      label: language === 'kn' ? '💰 ಮಾರುಕಟ್ಟೆ ಬೆಲೆ' : '💰 Market Prices',
      query: language === 'kn' ? 'ಇಂದಿನ ಟೊಮೆಟೊ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಎಷ್ಟು?' : 'What is today tomato market price in mandi?'
    },
    {
      icon: Landmark,
      label: language === 'kn' ? '🏛️ ಯೋಜನೆಗಳು' : '🏛️ Schemes',
      query: language === 'kn' ? 'ರೈತರಿಗೆ ಲಭ್ಯವಿರುವ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಯಾವುವು?' : 'What government schemes and subsidies are available for farmers?'
    }
  ];

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-2xl transition-all duration-300 transform hover:scale-105 flex items-center gap-2 group border border-white/20"
        aria-label={t('chat.openBtn') || 'Open AI Assistant'}
      >
        <div className="relative flex items-center justify-center">
          <MessageSquare className="w-6 h-6" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 border-2 border-primary-600 rounded-full animate-ping"></span>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 border-2 border-primary-600 rounded-full"></span>
        </div>
        <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 ease-in-out whitespace-nowrap text-sm font-semibold pr-1">
          {t('chat.openBtn') || 'AI Assistant'}
        </span>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 md:right-6 z-50 w-[calc(100vw-2rem)] md:w-96 h-[540px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-slideUp">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-3.5 text-white flex items-center justify-between shadow-md shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/30">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm leading-tight flex items-center gap-1.5">
                  <span>{t('chat.botName') || 'AgriMitra AI Assistant'}</span>
                  <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                </h3>
                <p className="text-[10px] text-primary-100 font-medium">
                  {language === 'kn' ? 'ಅಗ್ರಿಕಲ್ಚರಲ್ ಡಿಸಿಷನ್ ಅಸಿಸ್ಟೆಂಟ್ • ಆನ್‌ಲೈನ್' : 'Agricultural AI Assistant • Online'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={clearChat}
                title={language === 'kn' ? 'ಸಂಭಾಷಣೆ ಅಳಿಸಿ' : 'Clear Conversation'}
                className="p-1.5 hover:bg-white/20 rounded-lg transition-colors text-white"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:bg-white/20 rounded-lg transition-colors text-white"
                aria-label={t('chat.closeBtn') || 'Close'}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Messages Body */}
          <div className="flex-1 p-3.5 overflow-y-auto space-y-3 bg-gray-50/60">
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
                  className={`max-w-[84%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed whitespace-pre-line ${
                    msg.sender === 'user'
                      ? 'bg-primary-600 text-white rounded-br-none shadow-sm font-medium'
                      : 'bg-white text-gray-800 border border-gray-200/80 rounded-bl-none shadow-xs'
                  }`}
                >
                  <p>{msg.text}</p>
                  <span
                    className={`block text-[9px] mt-1.5 text-right ${
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

            {/* Loading Indicator */}
            {loading && (
              <div className="flex gap-2.5 justify-start">
                <div className="w-7 h-7 bg-primary-600 rounded-lg flex items-center justify-center shrink-0 text-white mt-1">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-4 py-3 shadow-xs flex items-center gap-2 text-xs text-gray-500 font-medium">
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-primary-600" />
                  <span>{language === 'kn' ? 'AI ಕೃಷಿ ಸಲಹೆ ಯೋಚಿಸುತ್ತಿದೆ...' : 'AI Assistant is thinking...'}</span>
                </div>
              </div>
            )}

            {/* Error Message & Retry */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 space-y-2">
                <p className="font-medium">{error}</p>
                <button
                  onClick={() => handleSend()}
                  className="flex items-center gap-1.5 text-[11px] font-semibold text-red-800 hover:text-red-900 underline"
                >
                  <RotateCcw className="w-3 h-3" />
                  {language === 'kn' ? 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ' : 'Try Again'}
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions Bar */}
          <div className="px-2.5 py-2 bg-white border-t border-gray-100 flex items-center gap-1.5 overflow-x-auto scrollbar-none shrink-0">
            {quickActions.map((qa, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(qa.query)}
                disabled={loading}
                className="px-2.5 py-1 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-lg text-[11px] font-semibold whitespace-nowrap transition-colors border border-primary-100/80 disabled:opacity-50"
              >
                {qa.label}
              </button>
            ))}
          </div>

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-2.5 bg-white border-t border-gray-200 flex items-center gap-2 shrink-0"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              placeholder={t('chat.placeholder') || (language === 'kn' ? 'ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ...' : 'Ask your farming question...')}
              className="flex-1 px-3 py-2 text-xs border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none resize-none max-h-20"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 bg-primary-600 hover:bg-primary-700 disabled:opacity-40 text-white rounded-xl transition-all shadow-xs shrink-0 flex items-center justify-center"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>
        </div>
      )}
    </>
  );
};
