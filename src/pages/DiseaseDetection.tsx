import { useState, useRef, useEffect } from 'react';
import { Upload, X, ScanLine, AlertCircle, CheckCircle, Leaf, Loader2 } from 'lucide-react';
import type { DiseasePrediction, UploadedImage } from '../types';
import { loadDiseaseModel, predictDisease, getSupportedCrops } from '../services/diseaseModel';

export default function DiseaseDetection() {
  const [uploadedImage, setUploadedImage] = useState<UploadedImage | null>(null);
  const [prediction, setPrediction] = useState<DiseasePrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    initializeModel();
  }, []);

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
      alert('Please upload an image file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage({
        file,
        preview: e.target?.result as string
      });
      setPrediction(null);
    };
    reader.readAsDataURL(file);
  }

  async function analyzeImage() {
    if (!uploadedImage) return;

    setLoading(true);
    try {
      const result = await predictDisease(uploadedImage.file);
      setPrediction(result);
    } catch (error) {
      console.error('Prediction error:', error);
    } finally {
      setLoading(false);
    }
  }

  function clearImage() {
    setUploadedImage(null);
    setPrediction(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }

  const supportedCrops = getSupportedCrops();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Leaf Disease Detection</h1>
        <p className="text-gray-500">AI-powered plant disease identification and treatment recommendations</p>
      </div>

      {/* Supported Crops */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Leaf className="w-5 h-5 text-green-500" />
          Supported Crops
        </h3>
        <div className="flex flex-wrap gap-2">
          {supportedCrops.map((crop) => (
            <span
              key={crop}
              className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm"
            >
              {crop}
            </span>
          ))}
        </div>
      </div>

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
              Upload Plant Image
            </h3>
            <p className="text-gray-500 mb-2">
              Drag and drop your image here, or click to browse
            </p>
            <p className="text-sm text-gray-400">
              Supports: JPG, PNG, WEBP (max 10MB)
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
                className="absolute top-2 right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
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
                    Analyzing...
                  </>
                ) : (
                  <>
                    <ScanLine className="w-5 h-5" />
                    Analyze Image
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
            {prediction.disease === 'Healthy Plant' ? (
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
            ) : (
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            )}
            <div>
              <h3 className="text-xl font-bold text-gray-900">{prediction.disease}</h3>
              <p className="text-gray-500">
                Confidence: <span className="font-semibold text-primary-600">{prediction.confidence}%</span>
              </p>
            </div>
          </div>

          <p className="text-gray-600 mb-6">{prediction.description}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Treatment */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-xs">
                  1
                </span>
                Treatment Recommendations
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
                <span className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center text-green-600 text-xs">
                  2
                </span>
                Prevention Measures
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

          {prediction.disease !== 'Healthy Plant' && (
            <div className="mt-6 p-4 bg-amber-50 rounded-lg">
              <p className="text-amber-800 text-sm">
                <strong>Note:</strong> This is an AI-based prediction. For confirmation and specific treatment advice, 
                please consult with your local agricultural extension officer or plant pathologist.
              </p>
            </div>
          )}

          <button
            onClick={clearImage}
            className="mt-6 btn-secondary w-full"
          >
            Analyze Another Image
          </button>
        </div>
      )}

      {/* Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Tips for Best Results</h3>
        <ul className="space-y-2 text-blue-800 text-sm">
          <li>• Take photos in good lighting conditions</li>
          <li>• Focus on the affected area of the leaf</li>
          <li>• Include both healthy and diseased parts for comparison</li>
          <li>• Avoid blurry or dark images</li>
          <li>• Capture multiple angles if possible</li>
        </ul>
      </div>
    </div>
  );
}
