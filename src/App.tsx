import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Weather from './pages/Weather';
import MarketPrices from './pages/MarketPrices';
import Schemes from './pages/Schemes';
import DiseaseDetection from './pages/DiseaseDetection';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="weather" element={<Weather />} />
          <Route path="market" element={<MarketPrices />} />
          <Route path="schemes" element={<Schemes />} />
          <Route path="disease" element={<DiseaseDetection />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
