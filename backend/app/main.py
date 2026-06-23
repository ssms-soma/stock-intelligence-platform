from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health_routes import router as health_router
from app.api.routes.stock_routes import router as stock_router
app = FastAPI(
    title="AI Stock Intelligence Platform API",
    description="Backend API for stock data, news, sentiment, agents, and RAG.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(stock_router, prefix="/api")