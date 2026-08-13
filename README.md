# Smart Agricultural Assistance System (AgroPulse)

A comprehensive AI-powered Smart Agricultural Assistance Platform designed to empower farmers with real-time weather insights, market price trends, government scheme recommendations, and crop disease detection.

## Project Structure

```
Smart-Agricultural-Assistance-System/
├── frontend/                  # React + TypeScript + Vite Frontend App
│   ├── src/                   # Source code (Components, Pages, Services, Contexts)
│   ├── public/                # Static public assets
│   ├── package.json           # Frontend dependencies & scripts
│   ├── vite.config.ts         # Vite configuration
│   └── tailwind.config.js     # Tailwind CSS setup
├── backend/                   # FastAPI / Python ML Backend
│   ├── app/                   # Backend routes, database models & API endpoints
│   ├── ml_models/             # Trained CNN disease classification models
│   ├── requirements.txt       # Python backend dependencies
│   └── smart_agri.db          # SQLite database
├── dataset/                   # Plant disease training datasets
├── uploads/                   # Temporary upload directory
└── vercel.json                # Vercel deployment configuration
```

## Quick Start

### 1. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend dashboard will run at `http://localhost:5173`.

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```
The FastAPI backend server will run at `http://localhost:8000`.

## Tech Stack
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React
- **Backend**: FastAPI, PyTorch / TensorFlow, SQLite, Uvicorn
- **APIs**: OpenWeatherMap API, Agmarknet Market Prices
