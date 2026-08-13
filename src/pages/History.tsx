import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { historyApi, type FarmerCombinedHistory } from '../services/historyApi';
import { History as HistoryIcon, ScanLine, Building2, Cloud, TrendingUp, Clock, AlertCircle, RefreshCw, Trash2, CheckCircle2 } from 'lucide-react';

export default function History() {
  const { token, user, isAuthenticated } = useAuth();
  const { language } = useLanguage();

  const [history, setHistory] = useState<FarmerCombinedHistory | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'disease' | 'schemes' | 'weather' | 'market'>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [deleting, setDeleting] = useState<boolean>(false);

  const fetchHistory = async () => {
    if (!token) {
      setHistory(null);
      setLoading(false);
      return;
    }
    setHistory(null);
    setLoading(true);
    setError('');
    try {
      const data = await historyApi.getCombinedHistory(token);
      setHistory(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load activity history.');
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = async () => {
    if (!token || !window.confirm(language === 'kn' ? 'ನಿಮ್ಮ ಎಲ್ಲಾ ಇತಿಹಾಸವನ್ನು ಅಳಿಸಲು ನೀವು ಖಚಿತವಾಗಿದ್ದೀರಾ?' : 'Are you sure you want to clear all your activity history?')) return;
    setDeleting(true);
    setError('');
    setSuccessMsg('');
    try {
      await historyApi.clearAllHistory(token);
      setSuccessMsg(language === 'kn' ? 'ನಿಮ್ಮ ಎಲ್ಲಾ ಚಟುವಟಿಕೆ ಇತಿಹಾಸವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ.' : 'All your activity history has been cleared successfully.');
      await fetchHistory();
    } catch (err: any) {
      setError(err.message || 'Failed to clear history.');
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteItem = async (category: 'disease' | 'schemes' | 'weather' | 'market', id: number) => {
    if (!token) return;
    setError('');
    setSuccessMsg('');
    try {
      await historyApi.deleteHistoryItem(token, category, id);
      setSuccessMsg(language === 'kn' ? 'ಇಂಟ್ರಿ ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ.' : 'History item deleted successfully.');
      await fetchHistory();
    } catch (err: any) {
      setError(err.message || 'Failed to delete item.');
    }
  };

  useEffect(() => {
    setHistory(null);
    if (isAuthenticated && token) {
      fetchHistory();
    } else {
      setSuccessMsg('');
      setLoading(false);
    }
  }, [isAuthenticated, token, user?.id]);

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto my-12 p-8 bg-white rounded-2xl shadow-lg text-center space-y-4">
        <HistoryIcon className="w-12 h-12 text-primary-600 mx-auto" />
        <h3 className="text-xl font-bold text-gray-900">
          {language === 'kn' ? 'ಖಾತೆ ಲಾಗಿನ್ ಅಗತ್ಯವಿದೆ' : 'Login Required'}
        </h3>
        <p className="text-sm text-gray-500">
          {language === 'kn' ? 'ನಿಮ್ಮ ಚಟುವಟಿಕೆ ಇತಿಹಾಸವನ್ನು ವೀಕ್ಷಿಸಲು ಲಾಗಿನ್ ಮಾಡಿ.' : 'Please sign in to view your complete activity history.'}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <HistoryIcon className="w-6 h-6 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">
              {language === 'kn' ? 'ನನ್ನ ಚಟುವಟಿಕೆ ಇತಿಹಾಸ (My History)' : 'Complete Farmer Activity History'}
            </h1>
          </div>
          <p className="text-xs text-gray-500">
            {language === 'kn'
              ? 'ರೋಗ ಪತ್ತೆ, ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು, ಹವಾಮಾನ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಶೋಧನೆಗಳ ಇತಿಹಾಸ'
              : 'Log of your plant disease diagnoses, government scheme checks, weather searches, and market prices.'}
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <button
            onClick={fetchHistory}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            <span>{language === 'kn' ? 'ಮರುಲೋಡ್ ಮಾಡಿ' : 'Refresh Logs'}</span>
          </button>

          <button
            onClick={handleClearAll}
            disabled={deleting || !history}
            className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-all border border-red-200 disabled:opacity-50"
          >
            <Trash2 className="w-4 h-4" />
            <span>{language === 'kn' ? 'ಇತಿಹಾಸ ಅಳಿಸಿ' : 'Clear All History'}</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
            activeTab === 'all'
              ? 'bg-primary-600 text-white shadow-md shadow-primary-200'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          }`}
        >
          {language === 'kn' ? 'ಎಲ್ಲಾ ಚಟುವಟಿಕೆಗಳು' : 'All Timeline Logs'} ({history?.recent_activities.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('disease')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeTab === 'disease'
              ? 'bg-primary-600 text-white shadow-md shadow-primary-200'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          }`}
        >
          <ScanLine className="w-4 h-4" />
          <span>{language === 'kn' ? 'ರೋಗ ಪತ್ತೆ ಇತಿಹಾಸ' : 'Disease History'}</span> ({history?.disease_history.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('schemes')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeTab === 'schemes'
              ? 'bg-primary-600 text-white shadow-md shadow-primary-200'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>{language === 'kn' ? 'ಯೋಜನೆಗಳ ಶೋಧನೆ' : 'Schemes History'}</span> ({history?.scheme_history.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('weather')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeTab === 'weather'
              ? 'bg-primary-600 text-white shadow-md shadow-primary-200'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          }`}
        >
          <Cloud className="w-4 h-4" />
          <span>{language === 'kn' ? 'ಹವಾಮಾನ ಇತಿಹಾಸ' : 'Weather History'}</span> ({history?.weather_history.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('market')}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 ${
            activeTab === 'market'
              ? 'bg-primary-600 text-white shadow-md shadow-primary-200'
              : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>{language === 'kn' ? 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಇತಿಹಾಸ' : 'Market History'}</span> ({history?.market_history.length || 0})
        </button>
      </div>

      {loading && (
        <div className="bg-white p-12 rounded-2xl border border-gray-200 text-center space-y-3">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-gray-500">{language === 'kn' ? 'ಇತಿಹಾಸವನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...' : 'Fetching farmer activity logs...'}</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="bg-green-50 border border-green-200 text-green-800 p-4 rounded-xl flex items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg('')} className="text-xs font-bold text-green-700 hover:underline">
            {language === 'kn' ? 'ಮುಚ್ಚಿ' : 'Dismiss'}
          </button>
        </div>
      )}

      {!loading && !error && history && (
        <div className="space-y-4">
          {/* TAB 1: ALL ACTIVITY TIMELINE */}
          {activeTab === 'all' && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4 shadow-xs">
              <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-primary-600" />
                <span>Recent Combined Activity Logs</span>
              </h3>

              {history.recent_activities.length === 0 ? (
                <p className="text-sm text-gray-500 py-6 text-center">No recent activities recorded yet.</p>
              ) : (
                <div className="space-y-3 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
                  {history.recent_activities.map((act) => (
                    <div key={act.id} className="relative pl-10 space-y-1">
                      <div className="absolute left-2 top-1.5 w-4 h-4 rounded-full bg-primary-600 border-2 border-white ring-2 ring-primary-100"></div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-bold text-gray-900">{act.title}</span>
                        <span className="text-xs text-gray-400">
                          {new Date(act.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600">{act.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: DISEASE HISTORY */}
          {activeTab === 'disease' && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4 shadow-xs">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <ScanLine className="w-5 h-5 text-primary-600" />
                <span>Plant Disease Detections Record</span>
              </h3>

              {history.disease_history.length === 0 ? (
                <p className="text-sm text-gray-500 py-6 text-center">No disease detections recorded yet.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {history.disease_history.map((item) => (
                    <div key={item.id} className="border border-gray-200 rounded-xl p-4 space-y-2 bg-gray-50/50 relative group">
                      <div className="flex items-center justify-between">
                        <span className="px-2.5 py-1 bg-green-100 text-green-800 font-bold text-xs rounded-lg">
                          {item.crop_type || 'Leaf'}
                        </span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">
                            {new Date(item.created_at).toLocaleDateString()}
                          </span>
                          <button
                            onClick={() => handleDeleteItem('disease', item.id)}
                            title="Delete entry"
                            className="p-1 hover:bg-red-100 text-gray-400 hover:text-red-600 rounded-md transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      <h4 className="text-sm font-bold text-gray-900">{item.detected_disease}</h4>
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <span>Confidence: <strong className="text-gray-900">{(item.confidence_score * 100).toFixed(1)}%</strong></span>
                        <span className="text-gray-400 font-mono text-[10px] truncate max-w-[150px]">{item.image_path}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: SCHEME HISTORY */}
          {activeTab === 'schemes' && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4 shadow-xs">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-primary-600" />
                <span>Government Scheme Searches & Recommendations Log</span>
              </h3>

              {history.scheme_history.length === 0 ? (
                <p className="text-sm text-gray-500 py-6 text-center">No scheme searches recorded yet.</p>
              ) : (
                <div className="space-y-3">
                  {history.scheme_history.map((item) => (
                    <div key={item.id} className="border border-gray-200 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-gray-50/50">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-primary-700 bg-primary-50 px-2 py-0.5 rounded uppercase">
                            {item.action_type}
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {item.scheme_name || item.search_query || 'General Scheme Search'}
                          </span>
                        </div>
                        {item.eligibility_status && (
                          <span className={`inline-block px-2 py-0.5 text-xs font-bold rounded ${
                            item.eligibility_status === 'Eligible' ? 'bg-green-100 text-green-800' :
                            item.eligibility_status === 'Partially matching' ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-700'
                          }`}>
                            Status: {item.eligibility_status}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400 shrink-0">
                          {new Date(item.created_at).toLocaleString()}
                        </span>
                        <button
                          onClick={() => handleDeleteItem('schemes', item.id)}
                          title="Delete entry"
                          className="p-1 hover:bg-red-100 text-gray-400 hover:text-red-600 rounded-md transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: WEATHER HISTORY */}
          {activeTab === 'weather' && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4 shadow-xs">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Cloud className="w-5 h-5 text-primary-600" />
                <span>Weather Searches Record</span>
              </h3>

              {history.weather_history.length === 0 ? (
                <p className="text-sm text-gray-500 py-6 text-center">No weather searches recorded yet.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {history.weather_history.map((item) => (
                    <div key={item.id} className="border border-gray-200 rounded-xl p-4 space-y-1 bg-gray-50/50">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-gray-900">{item.location_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{new Date(item.created_at).toLocaleDateString()}</span>
                          <button
                            onClick={() => handleDeleteItem('weather', item.id)}
                            title="Delete entry"
                            className="p-1 hover:bg-red-100 text-gray-400 hover:text-red-600 rounded-md transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      <p className="text-xs text-gray-600">{item.summary_text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 5: MARKET HISTORY */}
          {activeTab === 'market' && (
            <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-4 shadow-xs">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary-600" />
                <span>Market Price Queries Record</span>
              </h3>

              {history.market_history.length === 0 ? (
                <p className="text-sm text-gray-500 py-6 text-center">No market searches recorded yet.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {history.market_history.map((item) => (
                    <div key={item.id} className="border border-gray-200 rounded-xl p-4 space-y-1 bg-gray-50/50">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-bold text-gray-900">{item.crop_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{new Date(item.created_at).toLocaleDateString()}</span>
                          <button
                            onClick={() => handleDeleteItem('market', item.id)}
                            title="Delete entry"
                            className="p-1 hover:bg-red-100 text-gray-400 hover:text-red-600 rounded-md transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      <p className="text-xs text-gray-600">{item.summary_text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
