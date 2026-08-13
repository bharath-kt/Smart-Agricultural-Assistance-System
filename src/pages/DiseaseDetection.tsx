import { useState, useRef, useEffect } from 'react';
import { Upload, X, ScanLine, AlertCircle, CheckCircle, Leaf, Loader2 } from 'lucide-react';
import type { DiseasePrediction, UploadedImage } from '../types';
import { loadDiseaseModel, predictDisease, getSupportedCrops, translatePrediction, CROP_LOCALIZATION } from '../services/diseaseModel';
import { useLanguage } from '../contexts/LanguageContext';

import { useAuth } from '../contexts/AuthContext';

export default function DiseaseDetection() {
  const { language, t } = useLanguage();
  const { profile, token } = useAuth();
  const [uploadedImage, setUploadedImage] = useState<UploadedImage | null>(null);
  const [prediction, setPrediction] = useState<DiseasePrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState<string>('');
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    initializeModel();
    if (profile?.crops_grown && profile.crops_grown.length > 0) {
      const match = profile.crops_grown.find(c => ['Tomato', 'Corn', 'Paddy'].includes(c));
      if (match) setSelectedCrop(match);
    }
  }, [profile]);

  async function initializeModel() {
    const loaded = await loadDiseaseModel();
    setModelLoaded(loaded);
  }

  function handleDrag(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  }

  function handleFile(file: File) {
    if (!file.type.startsWith('image/')) {
      alert(t('disease.uploadAlert'));
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage({
        file,
        preview: e.target?.result as string
      });
      setPrediction(null);
      setError('');
    };
    reader.readAsDataURL(file);
  }

  async function analyzeImage() {
    if (!uploadedImage) return;

    if (!selectedCrop) {
      setError(t('disease.errorCropSelect'));
      return;
    }

    setLoading(true);
    setError('');
    try {
      const rawResult = await predictDisease(uploadedImage.file, selectedCrop, token || undefined);
      const result = translatePrediction(rawResult, language);
      setPrediction(result);
    } catch (err: any) {
      console.error('Prediction error:', err);
      setError(err.message || t('disease.analysisError'));
    } finally {
      setLoading(false);
    }
  }

  function clearImage() {
    setUploadedImage(null);
    setPrediction(null);
    setError('');
    setSelectedCrop('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  const supportedCrops = getSupportedCrops();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{t('disease.title')}</h1>
        <p className="text-gray-500">{t('disease.subtitle')}</p>
      </div>

      {/* Supported Crops */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Leaf className="w-5 h-5 text-green-500" />
          {t('disease.supportedCropsTitle')}
        </h3>
        <div className="flex flex-wrap gap-2">
          {supportedCrops.map((crop) => (
            <span
              key={crop}
              className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium"
            >
              {CROP_LOCALIZATION[crop]?.[language] || crop}
            </span>
          ))}
        </div>
      </div>

      {/* Crop Selection */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3">{t('disease.selectCropType')}</h3>
        <div className="flex gap-4">
          {supportedCrops.map((crop) => (
            <label
              key={crop}
              className={`flex-1 cursor-pointer border-2 rounded-xl p-4 text-center transition-all ${
                selectedCrop === crop
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
              }`}
            >
              <input
                type="radio"
                name="crop"
                value={crop}
                checked={selectedCrop === crop}
                onChange={(e) => {
                  setSelectedCrop(e.target.value);
                  setError('');
                }}
                className="hidden"
              />
              <span className="font-medium text-gray-900">
                {CROP_LOCALIZATION[crop]?.[language] || crop}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p className="font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* Upload Area */}
      <div className="card">
        {!uploadedImage ? (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
              transition-colors duration-200
              ${dragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {t('disease.uploadTitle')}
            </h3>
            <p className="text-gray-500 mb-2">
              {t('disease.uploadDragDrop')}
            </p>
            <p className="text-sm text-gray-400">
              {t('disease.supportsText')}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              <img
                src={uploadedImage.preview}
                alt="Uploaded plant"
                className="w-full max-h-96 object-contain rounded-lg"
              />
              <button
                onClick={clearImage}
                className="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {!prediction && (
              <button
                onClick={analyzeImage}
                disabled={loading || !modelLoaded}
                className="w-full btn-primary flex items-center justify-center gap-2 py-3"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {t('disease.analyzingBtn')}
                  </>
                ) : (
                  <>
                    <ScanLine className="w-5 h-5" />
                    {t('disease.analyzeBtn')}
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Prediction Results */}
      {prediction && (
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            {prediction.disease.includes('Healthy') ? (
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center shrink-0">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            ) : (
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center shrink-0">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            )}
            <div>
              <p className="text-sm text-gray-500">{prediction.plantName}</p>
              <h3 className="text-xl font-bold text-gray-900">{prediction.diseaseName}</h3>
              <p className="text-gray-500">
                {t('disease.confidenceLabel')}: <span className="font-semibold text-primary-600">{prediction.confidence}%</span>
              </p>
            </div>
          </div>

          <p className="text-gray-600 mb-6 leading-relaxed">{prediction.description}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Treatment */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-xs font-bold">
                  1
                </span>
                {t('disease.treatmentTitle')}
              </h4>
              <ul className="space-y-2">
                {prediction.treatment.map((item, idx) => (
                  <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                    <span className="text-blue-500 mt-1">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Prevention */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center text-green-600 text-xs font-bold">
                  2
                </span>
                {t('disease.preventionTitle')}
              </h4>
              <ul className="space-y-2">
                {prediction.prevention.map((item, idx) => (
                  <li key={idx} className="text-gray-600 text-sm flex items-start gap-2">
                    <span className="text-green-500 mt-1">•</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {!prediction.disease.includes('Healthy') && (
            <div className="mt-6 p-4 bg-amber-50 rounded-lg">
              <p className="text-amber-800 text-sm leading-relaxed">
                {t('disease.disclaimerNote')}
              </p>
            </div>
          )}

          <button
            onClick={clearImage}
            className="mt-6 btn-secondary w-full"
          >
            {t('disease.analyzeAnother')}
          </button>
        </div>
      )}

      {/* Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">{t('disease.tipsTitle')}</h3>
        <ul className="space-y-2 text-blue-800 text-sm">
          <li>{t('disease.tip1')}</li>
          <li>{t('disease.tip2')}</li>
          <li>{t('disease.tip3')}</li>
          <li>{t('disease.tip4')}</li>
          <li>{t('disease.tip5')}</li>
        </ul>
      </div>
    </div>
  );
}
