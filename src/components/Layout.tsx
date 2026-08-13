import { useState } from 'react';
import { NavLink, Outlet, Link, useNavigate } from 'react-router-dom';
import { 
  Cloud, 
  TrendingUp, 
  Building2, 
  ScanLine, 
  LayoutDashboard,
  Menu,
  X,
  Sprout,
  Globe,
  User,
  History,
  LogOut,
  LogIn
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { Chatbot } from './Chatbot';
import agriBg from '../assets/agriculture-bg.png';

export default function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { language, setLanguage, t } = useLanguage();
  const { isAuthenticated, user, profile, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', label: t('app.nav.dashboard'), icon: LayoutDashboard },
    { path: '/disease', label: t('app.nav.disease'), icon: ScanLine },
    { path: '/weather', label: t('app.nav.weather'), icon: Cloud },
    { path: '/market', label: t('app.nav.market'), icon: TrendingUp },
    { path: '/schemes', label: t('app.nav.schemes'), icon: Building2 },
    ...(isAuthenticated ? [
      { path: '/history', label: language === 'kn' ? 'ನನ್ನ ಇತಿಹಾಸ' : 'My History', icon: History },
      { path: '/profile', label: language === 'kn' ? 'ನನ್ನ ಪ್ರೊಫೈಲ್' : 'My Profile', icon: User }
    ] : [])
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center shrink-0 shadow-md shadow-primary-200">
                <Sprout className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h1 className="text-xl font-bold text-gray-900 truncate">{t('app.title')}</h1>
                <p className="text-xs text-gray-500 truncate">{t('app.subtitle')}</p>
              </div>
            </div>
          </div>

          {/* User Status Card */}
          {isAuthenticated ? (
            <div className="p-4 mx-4 mt-4 bg-primary-50 rounded-xl border border-primary-100 flex items-center justify-between">
              <div className="min-w-0">
                <p className="text-xs text-primary-600 font-semibold uppercase">{language === 'kn' ? 'ರೈತರ ಖಾತೆ' : 'Farmer Account'}</p>
                <p className="text-sm font-bold text-gray-900 truncate">{user?.full_name || 'Farmer'}</p>
                <p className="text-[11px] text-gray-500 truncate">{profile?.district || 'Mysuru'}, {profile?.state || 'Karnataka'}</p>
              </div>
              <button
                onClick={handleLogout}
                title="Logout"
                className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-white rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="p-4 mx-4 mt-4 bg-amber-50 rounded-xl border border-amber-100 space-y-2">
              <p className="text-xs text-amber-800 font-medium">
                {language === 'kn' ? 'ಖಾಸಗಿ ಯೋಜನೆ ಮತ್ತು ಇತಿಹಾಸಕ್ಕಾಗಿ ಲಾಗಿನ್ ಮಾಡಿ' : 'Sign in to save profile and get scheme recommendations'}
              </p>
              <Link
                to="/login"
                onClick={() => setIsSidebarOpen(false)}
                className="w-full py-2 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-lg text-xs flex items-center justify-center gap-1.5 shadow-xs"
              >
                <LogIn className="w-4 h-4" />
                <span>{language === 'kn' ? 'ಲಾಗಿನ್ / ನೋಂದಣಿ' : 'Login / Register'}</span>
              </Link>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsSidebarOpen(false)}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-4 py-3 rounded-xl
                    transition-all duration-200 text-sm font-medium
                    ${isActive 
                      ? 'bg-primary-600 text-white shadow-md shadow-primary-200' 
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  <span className="truncate">{item.label}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Sidebar Footer Language Switcher */}
          <div className="p-4 border-t border-gray-200 bg-gray-50/50">
            <div className="flex items-center justify-between gap-2 px-2 py-1.5 bg-white rounded-xl border border-gray-200 shadow-xs">
              <div className="flex items-center gap-2 text-gray-600 text-xs font-semibold">
                <Globe className="w-4 h-4 text-primary-600 shrink-0" />
                <span>{t('app.languageSelector')}</span>
              </div>
              <div className="flex items-center bg-gray-100 p-0.5 rounded-lg">
                <button
                  onClick={() => setLanguage('en')}
                  className={`px-2 py-1 text-xs font-bold rounded-md transition-all ${
                    language === 'en'
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  EN
                </button>
                <button
                  onClick={() => setLanguage('kn')}
                  className={`px-2 py-1 text-xs font-bold rounded-md transition-all ${
                    language === 'kn'
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  ಕನ್ನಡ
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header Bar */}
        <header className="bg-white border-b border-gray-200 px-4 lg:px-8 py-3 flex items-center justify-between sticky top-0 z-30 shadow-xs">
          {/* Mobile Left Section */}
          <div className="flex items-center gap-3 lg:hidden">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center shrink-0">
              <Sprout className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-gray-900 text-base">{t('app.title')}</span>
          </div>

          {/* Desktop Left Title */}
          <div className="hidden lg:flex items-center gap-2 text-xs text-gray-500 font-semibold">
            <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></span>
            <span>{t('app.subtitle')}</span>
          </div>

          {/* Right Header Section */}
          <div className="flex items-center gap-3">
            {/* Top Bar Language Selector */}
            <div className="flex items-center bg-gray-100 border border-gray-200 p-0.5 rounded-xl shadow-xs">
              <button
                onClick={() => setLanguage('en')}
                className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  language === 'en'
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage('kn')}
                className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  language === 'kn'
                    ? 'bg-primary-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ಕನ್ನಡ
              </button>
            </div>

            {/* Auth Action Top Button */}
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 border border-red-200 bg-red-50 text-red-700 hover:bg-red-100 text-xs font-bold rounded-xl transition-all"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </button>
            ) : (
              <Link
                to="/login"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-primary-600 text-white hover:bg-primary-700 text-xs font-bold rounded-xl shadow-sm transition-all"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Login</span>
              </Link>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 border border-gray-200 text-gray-700"
              aria-label="Toggle Navigation"
            >
              {isSidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main 
          className="flex-1 p-4 lg:p-8 overflow-auto relative bg-cover bg-center bg-no-repeat bg-fixed"
          style={{
            backgroundImage: `linear-gradient(135deg, rgba(255, 255, 255, 0.88) 0%, rgba(236, 253, 245, 0.82) 50%, rgba(255, 255, 255, 0.90) 100%), url(${agriBg})`
          }}
        >
          <Outlet />
        </main>
      </div>

      {/* Floating Chatbot Widget */}
      <Chatbot />
    </div>
  );
}
