import { useState, useMemo } from 'react';
import { Search, Building2, ExternalLink, ChevronDown, ChevronUp, FileText, Users, CheckCircle } from 'lucide-react';
import { governmentSchemes, getSchemesByCategory, searchSchemes } from '../services/schemesData';
// import type { GovernmentScheme } from '../types';

const categories = [
  { id: 'all', label: 'All Schemes' },
  { id: 'subsidy', label: 'Subsidies' },
  { id: 'loan', label: 'Loans' },
  { id: 'insurance', label: 'Insurance' },
  { id: 'training', label: 'Training' },
  { id: 'equipment', label: 'Equipment' },
];

export default function Schemes() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedScheme, setExpandedScheme] = useState<string | null>(null);

  const filteredSchemes = useMemo(() => {
    let schemes = getSchemesByCategory(selectedCategory);
    if (searchTerm.trim()) {
      schemes = searchSchemes(searchTerm).filter(s => 
        selectedCategory === 'all' || s.category === selectedCategory
      );
    }
    return schemes;
  }, [searchTerm, selectedCategory]);

  function toggleScheme(id: string) {
    setExpandedScheme(expandedScheme === id ? null : id);
  }

  function getCategoryColor(category: string): string {
    const colors: { [key: string]: string } = {
      subsidy: 'bg-green-100 text-green-700',
      loan: 'bg-blue-100 text-blue-700',
      insurance: 'bg-purple-100 text-purple-700',
      training: 'bg-orange-100 text-orange-700',
      equipment: 'bg-cyan-100 text-cyan-700',
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Government Schemes</h1>
          <p className="text-gray-500">Explore and apply for agricultural schemes and subsidies</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search schemes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10 w-full sm:w-64"
          />
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === cat.id
                ? 'bg-primary-500 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-3xl font-bold text-primary-600">{governmentSchemes.length}</p>
          <p className="text-sm text-gray-500">Total Schemes</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-green-600">
            {governmentSchemes.filter(s => s.category === 'subsidy').length}
          </p>
          <p className="text-sm text-gray-500">Subsidies</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-blue-600">
            {governmentSchemes.filter(s => s.category === 'loan').length}
          </p>
          <p className="text-sm text-gray-500">Loan Schemes</p>
        </div>
        <div className="card text-center">
          <p className="text-3xl font-bold text-purple-600">
            {governmentSchemes.filter(s => s.category === 'insurance').length}
          </p>
          <p className="text-sm text-gray-500">Insurance</p>
        </div>
      </div>

      {/* Schemes List */}
      <div className="space-y-4">
        {filteredSchemes.length === 0 ? (
          <div className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No schemes found matching your criteria</p>
          </div>
        ) : (
          filteredSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="card overflow-hidden transition-shadow hover:shadow-lg"
            >
              {/* Header */}
              <button
                onClick={() => toggleScheme(scheme.id)}
                className="w-full flex items-start justify-between p-6 text-left"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getCategoryColor(scheme.category)}`}>
                      {scheme.category}
                    </span>
                    {scheme.website && (
                      <a
                        href={scheme.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="text-primary-600 hover:text-primary-700 flex items-center gap-1 text-sm"
                      >
                        <ExternalLink className="w-3 h-3" />
                        Official Website
                      </a>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{scheme.title}</h3>
                  <p className="text-gray-500 mt-1">{scheme.description}</p>
                </div>
                <div className="ml-4">
                  {expandedScheme === scheme.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </button>

              {/* Expanded Content */}
              {expandedScheme === scheme.id && (
                <div className="px-6 pb-6 border-t border-gray-100 pt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Benefits */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <h4 className="font-semibold text-gray-900">Benefits</h4>
                      </div>
                      <p className="text-gray-600 text-sm">{scheme.benefits}</p>
                    </div>

                    {/* Eligibility */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Users className="w-5 h-5 text-blue-500" />
                        <h4 className="font-semibold text-gray-900">Eligibility</h4>
                      </div>
                      <ul className="space-y-1">
                        {scheme.eligibility.map((item, idx) => (
                          <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                            <span className="text-primary-500 mt-1">•</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Application Process */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-5 h-5 text-purple-500" />
                        <h4 className="font-semibold text-gray-900">Application Process</h4>
                      </div>
                      <p className="text-gray-600 text-sm">{scheme.applicationProcess}</p>
                    </div>

                    {/* Documents Required */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-5 h-5 text-orange-500" />
                        <h4 className="font-semibold text-gray-900">Documents Required</h4>
                      </div>
                      <ul className="space-y-1">
                        {scheme.documents.map((doc, idx) => (
                          <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                            <span className="text-primary-500 mt-1">•</span>
                            {doc}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {scheme.deadline && (
                    <div className="mt-4 p-3 bg-amber-50 rounded-lg">
                      <p className="text-amber-800 text-sm">
                        <strong>Application Deadline:</strong> {scheme.deadline}
                      </p>
                    </div>
                  )}

                  {scheme.website && (
                    <div className="mt-4">
                      <a
                        href={scheme.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-primary inline-flex items-center gap-2"
                      >
                        Apply Now
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
