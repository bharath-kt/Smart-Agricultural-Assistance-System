import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Weather from './pages/Weather';
import MarketPrices from './pages/MarketPrices';
import Schemes from './pages/Schemes';
import DiseaseDetection from './pages/DiseaseDetection';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Profile from './pages/Profile';
import History from './pages/History';
import { LanguageProvider, useLanguage } from './contexts/LanguageContext';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageSelectionModal } from './components/LanguageSelectionModal';

function AppContent() {
  const { hasSelectedLanguage } = useLanguage();

  return (
    <>
      {!hasSelectedLanguage && (
        <LanguageSelectionModal onComplete={() => {}} />
      )}
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="weather" element={<Weather />} />
            <Route path="market" element={<MarketPrices />} />
            <Route path="schemes" element={<Schemes />} />
            <Route path="disease" element={<DiseaseDetection />} />
            <Route path="login" element={<Login />} />
            <Route path="signup" element={<Signup />} />
            <Route path="profile" element={<Profile />} />
            <Route path="history" element={<History />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
