import { useState, useRef, useEffect } from 'react';
import {
  Upload,
  X,
  ScanLine,
  AlertCircle,
  CheckCircle,
  Leaf,
  Loader2
} from 'lucide-react';

import type { DiseasePrediction, UploadedImage } from '../types';

import {
  loadDiseaseModel,
  predictDisease,
  getSupportedCrops,
  translatePrediction,
  CROP_LOCALIZATION
} from '../services/diseaseModel';

import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';

export default function DiseaseDetection() {
  const { language, t } = useLanguage();
  const { profile, token } = useAuth();

  const [uploadedImage, setUploadedImage] =
    useState<UploadedImage | null>(null);

  const [prediction, setPrediction] =
    useState<DiseasePrediction | null>(null);

  const [loading, setLoading] = useState(false);

  const [, setModelLoaded] =
    useState(false);

  const [dragActive, setDragActive] =
    useState(false);

  const [selectedCrop, setSelectedCrop] =
    useState<string>('');

  const [error, setError] =
    useState<string>('');

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  // ---------------------------------------------------------
  // INITIALIZE DISEASE SERVICE
  // ---------------------------------------------------------

  useEffect(() => {
    initializeModel();
  }, []);

  // Set crop from user's profile when available
  useEffect(() => {
    if (
      profile?.crops_grown &&
      profile.crops_grown.length > 0
    ) {
      const match = profile.crops_grown.find(
        (crop) =>
          ['Tomato', 'Corn', 'Paddy'].includes(crop)
      );

      if (match) {
        setSelectedCrop(match);
      }
    }
  }, [profile]);

  async function initializeModel() {
    try {
      await loadDiseaseModel();

      // The actual ML model runs on the backend.
      // The frontend only needs the disease service to be ready.
      setModelLoaded(true);
    } catch (error) {
      console.error(
        'Failed to initialize disease service:',
        error
      );

      // Keep the UI usable because the backend
      // performs the actual prediction.
      setModelLoaded(true);
    }
  }

  // ---------------------------------------------------------
  // DRAG AND DROP
  // ---------------------------------------------------------

  function handleDrag(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();

    if (
      e.type === 'dragenter' ||
      e.type === 'dragover'
    ) {
      setDragActive(true);
    } else if (
      e.type === 'dragleave'
    ) {
      setDragActive(false);
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    e.stopPropagation();

    setDragActive(false);

    if (
      e.dataTransfer.files &&
      e.dataTransfer.files[0]
    ) {
      handleFile(e.dataTransfer.files[0]);
    }
  }

  // ---------------------------------------------------------
  // FILE SELECTION
  // ---------------------------------------------------------

  function handleFileSelect(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    if (
      e.target.files &&
      e.target.files[0]
    ) {
      handleFile(e.target.files[0]);
    }
  }

  function handleFile(file: File) {
    if (!file.type.startsWith('image/')) {
      setError(t('disease.uploadAlert'));
      return;
    }

    // Optional file size protection
    if (file.size > 10 * 1024 * 1024) {
      setError(
        'Image size must be less than 10 MB.'
      );
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

  // ---------------------------------------------------------
  // ANALYZE IMAGE
  // ---------------------------------------------------------

  async function analyzeImage() {
    if (!uploadedImage) {
      setError(
        'Please upload a plant leaf image.'
      );
      return;
    }

    // VERY IMPORTANT:
    // Do not allow prediction without crop selection.
    if (!selectedCrop) {
      setError(
        t('disease.errorCropSelect')
      );
      return;
    }

    // Validate selected crop
    const supportedCrops = getSupportedCrops();

    if (!supportedCrops.includes(selectedCrop)) {
      setError(
        'Please select a valid crop: Tomato, Corn, or Paddy.'
      );
      return;
    }

    setLoading(true);
    setError('');
    setPrediction(null);

    try {
      console.log(
        'Starting disease detection...'
      );

      console.log(
        'Selected crop:',
        selectedCrop
      );

      console.log(
        'Image:',
        uploadedImage.file.name
      );

      // -----------------------------------------------------
      // SEND SELECTED CROP TO BACKEND
      // -----------------------------------------------------

      const rawResult = await predictDisease(
        uploadedImage.file,
        selectedCrop,
        token || undefined
      );

      console.log(
        'Disease API result:',
        rawResult
      );

      // -----------------------------------------------------
      // HANDLE BACKEND ERROR
      // -----------------------------------------------------

      if (
        !rawResult ||
        !rawResult.diseaseName
      ) {
        throw new Error(
          'The disease detection service did not return a valid prediction.'
        );
      }

      // -----------------------------------------------------
      // TRANSLATE RESULT IF KANNADA SELECTED
      // -----------------------------------------------------

      const result =
        translatePrediction(
          rawResult,
          language
        );

      setPrediction(result);

    } catch (err: unknown) {
      console.error(
        'Prediction error:',
        err
      );

      if (err instanceof Error) {
        setError(
          err.message ||
          t('disease.analysisError')
        );
      } else {
        setError(
          t('disease.analysisError')
        );
      }
    } finally {
      setLoading(false);
    }
  }

  // ---------------------------------------------------------
  // CLEAR IMAGE
  // ---------------------------------------------------------

  function clearImage() {
    setUploadedImage(null);
    setPrediction(null);
    setError('');
    setSelectedCrop('');

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  // ---------------------------------------------------------
  // SUPPORTED CROPS
  // ---------------------------------------------------------

  const supportedCrops =
    getSupportedCrops();

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="space-y-6">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {t('disease.title')}
        </h1>

        <p className="text-gray-500">
          {t('disease.subtitle')}
        </p>
      </div>

      {/* =====================================================
          SUPPORTED CROPS
      ===================================================== */}

      <div className="card">

        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">

          <Leaf className="w-5 h-5 text-green-500" />

          {t('disease.supportedCropsTitle')}

        </h3>

        <div className="flex flex-wrap gap-2">

          {supportedCrops.map(
            (crop) => (
              <span
                key={crop}
                className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium"
              >
                {
                  CROP_LOCALIZATION[crop]?.[
                  language
                  ] || crop
                }
              </span>
            )
          )}

        </div>
      </div>

      {/* =====================================================
          CROP SELECTION
      ===================================================== */}

      <div className="card">

        <h3 className="font-semibold text-gray-900 mb-3">
          {t('disease.selectCropType')}
        </h3>

        <div className="flex gap-4">

          {supportedCrops.map(
            (crop) => (

              <label
                key={crop}
                className={`flex-1 cursor-pointer border-2 rounded-xl p-4 text-center transition-all ${selectedCrop === crop
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
                  }`}
              >

                <input
                  type="radio"
                  name="crop"
                  value={crop}
                  checked={
                    selectedCrop === crop
                  }
                  onChange={(e) => {
                    setSelectedCrop(
                      e.target.value
                    );

                    setError('');
                    setPrediction(null);
                  }}
                  className="hidden"
                />

                <span className="font-medium text-gray-900">

                  {
                    CROP_LOCALIZATION[
                    crop
                    ]?.[language] || crop
                  }

                </span>

              </label>
            )
          )}

        </div>

        {/* Selected crop confirmation */}

        {selectedCrop && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">

            <p className="text-sm text-green-800">

              <strong>
                Selected crop:
              </strong>{' '}

              {
                CROP_LOCALIZATION[
                selectedCrop
                ]?.[language] ||
                selectedCrop
              }

            </p>

          </div>
        )}

      </div>

      {/* =====================================================
          ERROR
      ===================================================== */}

      {error && (

        <div className="card bg-red-50 border-red-200">

          <div className="flex items-center gap-2 text-red-700">

            <AlertCircle className="w-5 h-5 shrink-0" />

            <p className="font-medium">
              {error}
            </p>

          </div>

        </div>

      )}

      {/* =====================================================
          UPLOAD AREA
      ===================================================== */}

      <div className="card">

        {!uploadedImage ? (

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() =>
              fileInputRef.current?.click()
            }
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

            {/* IMAGE PREVIEW */}

            <div className="relative">

              <img
                src={uploadedImage.preview}
                alt="Uploaded plant leaf"
                className="w-full max-h-96 object-contain rounded-lg"
              />

              <button
                type="button"
                onClick={clearImage}
                className="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-md"
              >

                <X className="w-5 h-5" />

              </button>

            </div>

            {/* IMAGE INFORMATION */}

            <div className="p-3 bg-gray-50 rounded-lg">

              <p className="text-sm text-gray-600">

                <strong>
                  Image:
                </strong>{' '}

                {uploadedImage.file.name}

              </p>

              <p className="text-sm text-gray-600 mt-1">

                <strong>
                  Crop:
                </strong>{' '}

                {
                  CROP_LOCALIZATION[
                  selectedCrop
                  ]?.[language] ||
                  selectedCrop ||
                  'Not selected'
                }

              </p>

            </div>

            {/* ANALYZE BUTTON */}

            {!prediction && (

              <button
                type="button"
                onClick={analyzeImage}
                disabled={loading}
                className="w-full btn-primary flex items-center justify-center gap-2 py-3 disabled:opacity-60 disabled:cursor-not-allowed"
              >

                {loading ? (

                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />

                    {t(
                      'disease.analyzingBtn'
                    )}
                  </>

                ) : (

                  <>
                    <ScanLine className="w-5 h-5" />

                    {t(
                      'disease.analyzeBtn'
                    )}
                  </>

                )}

              </button>

            )}

          </div>

        )}

      </div>

      {/* =====================================================
          PREDICTION RESULT
      ===================================================== */}

      {prediction && (

        <div className="card">

          {/* RESULT HEADER */}

          <div className="flex items-center gap-3 mb-4">

            {prediction.disease.includes(
              'Healthy'
            ) ? (

              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center shrink-0">

                <CheckCircle className="w-6 h-6 text-green-600" />

              </div>

            ) : (

              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center shrink-0">

                <AlertCircle className="w-6 h-6 text-red-600" />

              </div>

            )}

            <div>

              <p className="text-sm text-gray-500">

                {prediction.plantName}

              </p>

              <h3 className="text-xl font-bold text-gray-900">

                {prediction.diseaseName}

              </h3>

              <p className="text-gray-500">

                {t(
                  'disease.confidenceLabel'
                )}:{' '}

                <span className="font-semibold text-primary-600">

                  {prediction.confidence}%

                </span>

              </p>

            </div>

          </div>

          {/* DESCRIPTION */}

          <p className="text-gray-600 mb-6 leading-relaxed">

            {prediction.description}

          </p>

          {/* TREATMENT + PREVENTION */}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* TREATMENT */}

            <div>

              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">

                <span className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-xs font-bold">
                  1
                </span>

                {t(
                  'disease.treatmentTitle'
                )}

              </h4>

              <ul className="space-y-2">

                {prediction.treatment.map(
                  (item, idx) => (

                    <li
                      key={idx}
                      className="text-gray-600 text-sm flex items-start gap-2"
                    >

                      <span className="text-blue-500 mt-1">
                        •
                      </span>

                      {item}

                    </li>

                  )
                )}

              </ul>

            </div>

            {/* PREVENTION */}

            <div>

              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">

                <span className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center text-green-600 text-xs font-bold">
                  2
                </span>

                {t(
                  'disease.preventionTitle'
                )}

              </h4>

              <ul className="space-y-2">

                {prediction.prevention.map(
                  (item, idx) => (

                    <li
                      key={idx}
                      className="text-gray-600 text-sm flex items-start gap-2"
                    >

                      <span className="text-green-500 mt-1">
                        •
                      </span>

                      {item}

                    </li>

                  )
                )}

              </ul>

            </div>

          </div>

          {/* DISCLAIMER */}

          {!prediction.disease.includes(
            'Healthy'
          ) && (

              <div className="mt-6 p-4 bg-amber-50 rounded-lg">

                <p className="text-amber-800 text-sm leading-relaxed">

                  {t(
                    'disease.disclaimerNote'
                  )}

                </p>

              </div>

            )}

          {/* ANALYZE ANOTHER */}

          <button
            type="button"
            onClick={clearImage}
            className="mt-6 btn-secondary w-full"
          >

            {t(
              'disease.analyzeAnother'
            )}

          </button>

        </div>

      )}

      {/* =====================================================
          TIPS
      ===================================================== */}

      <div className="card bg-blue-50 border-blue-200">

        <h3 className="font-semibold text-blue-900 mb-2">

          {t('disease.tipsTitle')}

        </h3>

        <ul className="space-y-2 text-blue-800 text-sm">

          <li>
            {t('disease.tip1')}
          </li>

          <li>
            {t('disease.tip2')}
          </li>

          <li>
            {t('disease.tip3')}
          </li>

          <li>
            {t('disease.tip4')}
          </li>

          <li>
            {t('disease.tip5')}
          </li>

        </ul>

      </div>

    </div>
  );
}