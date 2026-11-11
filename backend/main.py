import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from ai.explanation import llm_available  # noqa: E402
from backend.routes.products import router as products_router  # noqa: E402
from backend.routes.recommend import router as recommend_router  # noqa: E402

DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"

app = FastAPI(
    title="PriceSense AI",
    description="Compares sample grocery prices across quick-commerce platforms "
    "and explains where to buy.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", DEFAULT_ORIGINS).split(",")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/", tags=["Meta"])
def root():
    return {"message": "PriceSense backend running", "docs": "/docs"}


@app.get("/health", tags=["Meta"])
def health():
    return {"status": "ok", "llm_explanations": llm_available(), "demo_data": True}


app.include_router(products_router, tags=["Catalog"])
app.include_router(recommend_router, tags=["Recommend"])
