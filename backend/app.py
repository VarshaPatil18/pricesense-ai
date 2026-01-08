from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.products import router as products_router
from routes.recommend import router as recommend_router

app = FastAPI(title="PriceSense AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend access
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router, prefix="/products")
app.include_router(recommend_router, prefix="/recommend")
