from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.company_routes import router as company_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.news_routes import router as news_router
from app.api.routes.recommendation_routes import router as recommendation_router
from app.api.routes.research_routes import router as research_router
from app.api.routes.router_routes import router as router_router
from app.api.routes.sentiment_routes import router as sentiment_router
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
app.include_router(company_router, prefix="/api")
app.include_router(news_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(router_router, prefix="/api")
app.include_router(sentiment_router, prefix="/api")
