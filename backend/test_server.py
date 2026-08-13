"""Minimal test server to verify FastAPI setup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart Agriculture API - Test",
    description="Test server to verify FastAPI setup",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Smart Agriculture API is running!",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Smart Agriculture API",
        "version": "1.0.0"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "API v1 is working!",
        "endpoints": [
            "/api/v1/weather",
            "/api/v1/market",
            "/api/v1/disease",
            "/api/v1/schemes"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting test server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)
