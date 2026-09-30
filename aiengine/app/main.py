from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.anomaly import router as anomaly_router
from app.routes.explanation import router as explanation_router
from app.routes.intelligence import router as intelligence_router
from app.routes.inference import router as inference_router
from app.routes.review import router as review_router
from app.routes.response import router as response_router

app = FastAPI(
    title="THERMOS AI Intelligence Engine",
    description="Operational Thermal Intelligence, 6-Class Detection, SHAP Explainability & Digital Twins",
    version="2.0.0"
)

# Enable CORS for Command Center Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "online",
        "system": "THERMOS AI Engine",
        "version": "2.0.0",
        "model": "Multi-Class Calibrated XGBoost",
        "accuracy": "99.6%",
        "classes": [
            "INDUSTRIAL_FLARE",
            "INDUSTRIAL_FIRE",
            "MINING",
            "AGRICULTURAL",
            "WILDFIRE",
            "UNCLASSIFIED"
        ]
    }


app.include_router(
    intelligence_router,
    prefix="/api/v1/intelligence",
    tags=["Intelligence & Command Center"]
)

app.include_router(
    inference_router,
    prefix="/api/v1/inference",
    tags=["Real-Time AI Inference"]
)

app.include_router(
    anomaly_router,
    prefix="/api/v1/anomaly",
    tags=["Anomaly"]
)

app.include_router(
    explanation_router,
    prefix="/api/v1/explanation",
    tags=["Explanation"]
)

app.include_router(
    review_router,
    prefix="/api/v1/review",
    tags=["Human-in-the-Loop Review"]
)

app.include_router(
    response_router,
    prefix="/api/v1/response",
    tags=["Closed-Loop Emergency Response"]
)
