import { useState, useEffect, useMemo } from 'react';
import { Search, Building2, ExternalLink, ChevronDown, ChevronUp, FileText, Users, CheckCircle, AlertTriangle, XCircle, Info, Sparkles } from 'lucide-react';
import { getSchemesByCategory, searchSchemes, getLocalizedScheme, translateSchemeCategory, fetchBackendRecommendations, fetchBackendSchemes } from '../services/schemesData';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

export default function Schemes() {
  const { language, t } = useLanguage();
  const { isAuthenticated, token, profile } = useAuth();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedScheme, setExpandedScheme] = useState<number | string | null>(null);

  const [backendRecommendations, setBackendRecommendations] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSchemesData();
  }, [token, isAuthenticated]);

  async function loadSchemesData() {
    setLoading(true);
    try {
      if (token && isAuthenticated) {
        const recs = await fetchBackendRecommendations(token);
        setBackendRecommendations(recs);
      } else {
        await fetchBackendSchemes();
      }
    } catch (err) {
      console.error('Error fetching scheme engine recommendations:', err);
    } finally {
      setLoading(false);
    }
  }

  const categories = [
    { id: 'all', label: t('schemes.categories.all') },
    { id: 'subsidy', label: t('schemes.categories.subsidy') },
    { id: 'loan', label: t('schemes.categories.loan') },
    { id: 'insurance', label: t('schemes.categories.insurance') },
    { id: 'training', label: t('schemes.categories.training') },
    { id: 'equipment', label: t('schemes.categories.equipment') },
  ];

  function toggleScheme(id: number | string) {
    setExpandedScheme(expandedScheme === id ? null : id);
  }

  function getStatusBadge(status: string) {
    switch (status) {
      case 'Eligible':
        return (
          <span className="px-3 py-1 bg-green-100 text-green-800 border border-green-200 rounded-full text-xs font-bold flex items-center gap-1">
            <CheckCircle className="w-3.5 h-3.5 text-green-600" />
            <span>Eligible based on profile</span>
          </span>
        );
      case 'Partially matching':
        return (
          <span className="px-3 py-1 bg-amber-100 text-amber-800 border border-amber-200 rounded-full text-xs font-bold flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            <span>Partially matching / Condition check required</span>
          </span>
        );
      case 'Not eligible':
        return (
          <span className="px-3 py-1 bg-gray-100 text-gray-700 border border-gray-200 rounded-full text-xs font-bold flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5 text-gray-500" />
            <span>Not eligible</span>
          </span>
        );
      default:
        return null;
    }
  }

  // Recommendations processing if logged in
  const filteredRecommendations = useMemo(() => {
    if (!backendRecommendations || !backendRecommendations.recommendations) return [];
    let items = backendRecommendations.recommendations;
    if (selectedCategory !== 'all') {
      items = items.filter((item: any) => item.scheme.category === selectedCategory);
    }
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      items = items.filter((item: any) =>
        item.scheme.name.toLowerCase().includes(q) ||
        (item.scheme.short_description && item.scheme.short_description.toLowerCase().includes(q))
      );
    }
    return items;
  }, [backendRecommendations, selectedCategory, searchTerm]);

  // Fallback schemes if offline/guest
  const filteredGuestSchemes = useMemo(() => {
    let list = getSchemesByCategory(selectedCategory);
    if (searchTerm.trim()) {
      list = searchSchemes(searchTerm).filter(s => selectedCategory === 'all' || s.category === selectedCategory);
    }
    return list.map(s => getLocalizedScheme(s, language));
  }, [selectedCategory, searchTerm, language]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('schemes.title')}</h1>
          <p className="text-gray-500">{t('schemes.subtitle')}</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder={t('schemes.searchPlaceholder')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10 w-full sm:w-72"
          />
        </div>
      </div>

      {/* Authenticated Farmer Profile Match Summary */}
      {isAuthenticated && backendRecommendations && (
        <div className="bg-gradient-to-r from-primary-900 via-primary-800 to-indigo-900 text-white rounded-2xl p-6 shadow-xl space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-300" />
              <span className="font-bold text-sm tracking-wider uppercase text-amber-300">
                Eligibility Engine Analysis
              </span>
            </div>
            <span className="text-xs text-primary-200">
              Evaluated against Farmer Profile ({profile?.district}, {profile?.state})
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 text-center border border-white/10">
              <p className="text-2xl font-bold text-green-300">{backendRecommendations.eligible_count}</p>
              <p className="text-xs text-primary-100">Eligible Schemes</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 text-center border border-white/10">
              <p className="text-2xl font-bold text-amber-300">{backendRecommendations.partial_count}</p>
              <p className="text-xs text-primary-100">Partially Matching</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 text-center border border-white/10">
              <p className="text-2xl font-bold text-gray-300">{backendRecommendations.not_eligible_count}</p>
              <p className="text-xs text-primary-100">Not Eligible</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 text-center border border-white/10">
              <p className="text-2xl font-bold text-white">{backendRecommendations.total_schemes}</p>
              <p className="text-xs text-primary-100">Total Evaluated</p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-amber-200 pt-2 border-t border-white/10">
            <Info className="w-4 h-4 shrink-0 text-amber-300" />
            <span>{backendRecommendations.disclaimer}</span>
          </div>
        </div>
      )}

      {/* Guest Login Hint */}
      {!isAuthenticated && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-center justify-between text-sm text-amber-900 flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5 text-amber-600 shrink-0" />
            <span>Log in to check personalized scheme eligibility based on your land holding, crops, state, and category.</span>
          </div>
          <Link to="/login" className="px-4 py-2 bg-amber-600 text-white rounded-xl font-bold text-xs hover:bg-amber-700">
            Sign In to Check Eligibility
          </Link>
        </div>
      )}

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              selectedCategory === cat.id
                ? 'bg-primary-600 text-white shadow-sm'
                : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="py-12 text-center space-y-3">
          <div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-gray-500">Comparing farmer profile with scheme eligibility rules...</p>
        </div>
      )}

      {/* RECOMMENDATIONS SCHEME LIST (AUTHENTICATED) */}
      {!loading && isAuthenticated && backendRecommendations && (
        <div className="space-y-4">
          {filteredRecommendations.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-2xl border border-gray-200">
              <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">{t('schemes.emptyState')}</p>
            </div>
          ) : (
            filteredRecommendations.map((item: any) => {
              const scheme = item.scheme;
              const isExpanded = expandedScheme === scheme.id;
              return (
                <div key={scheme.id} className="card overflow-hidden transition-all border border-gray-200 hover:border-primary-300">
                  <button
                    onClick={() => toggleScheme(scheme.id)}
                    className="w-full flex items-start justify-between p-6 text-left space-y-2"
                  >
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3 flex-wrap">
                        {getStatusBadge(item.status)}
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 uppercase">
                          {scheme.government_level} • {scheme.category}
                        </span>
                        {scheme.official_website && (
                          <a
                            href={scheme.official_website}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-primary-600 hover:underline text-xs font-bold flex items-center gap-1 ml-auto"
                          >
                            <span>Official Portal</span>
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>

                      <h3 className="text-lg font-bold text-gray-900">{scheme.name}</h3>
                      <p className="text-sm text-gray-600">{scheme.short_description}</p>
                    </div>

                    <div className="ml-4 pt-1">
                      {isExpanded ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                    </div>
                  </button>

                  {/* Expanded Recommendation Details */}
                  {isExpanded && (
                    <div className="px-6 pb-6 border-t border-gray-100 pt-4 space-y-6">
                      {/* Match Breakdown Box */}
                      <div className="bg-gray-50 p-4 rounded-xl space-y-2 border border-gray-200">
                        <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                          Why Your Profile Matches ({item.match_score}% Score):
                        </h4>
                        <ul className="space-y-1">
                          {item.match_reasons.map((reason: string, idx: number) => (
                            <li key={idx} className="text-xs text-green-700 flex items-center gap-2 font-medium">
                              <CheckCircle className="w-3.5 h-3.5 shrink-0 text-green-600" />
                              <span>{reason}</span>
                            </li>
                          ))}
                          {item.missing_criteria.map((miss: string, idx: number) => (
                            <li key={idx} className="text-xs text-amber-700 flex items-center gap-2 font-medium">
                              <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-amber-600" />
                              <span>{miss}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-bold text-gray-900 text-sm mb-1 flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-green-600" />
                            Benefits Provided
                          </h4>
                          <p className="text-xs text-gray-600 leading-relaxed">{scheme.benefit_description || scheme.benefit_amount}</p>
                        </div>

                        <div>
                          <h4 className="font-bold text-gray-900 text-sm mb-1 flex items-center gap-2">
                            <Users className="w-4 h-4 text-blue-600" />
                            Eligibility Summary
                          </h4>
                          <p className="text-xs text-gray-600 leading-relaxed">{scheme.eligibility_summary || 'Available to eligible farmers'}</p>
                        </div>

                        <div>
                          <h4 className="font-bold text-gray-900 text-sm mb-1 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-purple-600" />
                            Application Procedure
                          </h4>
                          <p className="text-xs text-gray-600 leading-relaxed">{scheme.application_process}</p>
                        </div>

                        <div>
                          <h4 className="font-bold text-gray-900 text-sm mb-1 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-orange-600" />
                            Required Documents
                          </h4>
                          <ul className="space-y-1">
                            {item.required_documents.map((doc: string, idx: number) => (
                              <li key={idx} className="text-xs text-gray-600 flex items-center gap-1.5">
                                <span className="text-primary-500">•</span>
                                {doc}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div className="pt-3 border-t border-gray-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-gray-500">
                        <span>Last Updated: {scheme.last_updated_date || 'August 2026'}</span>
                        {scheme.official_website && (
                          <a
                            href={scheme.official_website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-primary inline-flex items-center gap-2 text-xs py-2 px-4"
                          >
                            <span>Apply on Official Portal</span>
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* GUEST SCHEME LIST */}
      {!loading && !isAuthenticated && (
        <div className="space-y-4">
          {filteredGuestSchemes.map((scheme) => (
            <div key={scheme.id} className="card overflow-hidden border border-gray-200">
              <button onClick={() => toggleScheme(scheme.id)} className="w-full flex items-start justify-between p-6 text-left">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700 capitalize">
                      {translateSchemeCategory(scheme.category, language)}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{scheme.title}</h3>
                  <p className="text-gray-500 mt-1">{scheme.description}</p>
                </div>
                <div className="ml-4 pt-1">
                  {expandedScheme === scheme.id ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
                </div>
              </button>

              {expandedScheme === scheme.id && (
                <div className="px-6 pb-6 border-t border-gray-100 pt-4 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-1">{t('schemes.benefits')}</h4>
                      <p className="text-gray-600 text-sm">{scheme.benefits}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 text-sm mb-1">{t('schemes.applicationProcess')}</h4>
                      <p className="text-gray-600 text-sm">{scheme.applicationProcess}</p>
                    </div>
                  </div>
                  {scheme.website && (
                    <a href={scheme.website} target="_blank" rel="noopener noreferrer" className="btn-primary inline-flex items-center gap-2 text-xs">
                      {t('schemes.applyNow')} <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
