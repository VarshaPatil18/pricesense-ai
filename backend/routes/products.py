from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query

from backend import catalog

router = APIRouter()


@router.get("/products")
def list_products(
    q: str = Query("", max_length=60, description="Name, brand or alias"),
    category: str | None = Query(None, max_length=40),
    limit: int = Query(20, ge=1, le=100),
):
    results = catalog.search(q, category, limit)
    return {"count": len(results), "products": [catalog.public_product(p) for p in results]}


@router.get("/products/{product_id}")
def get_product(product_id: str):
    product = catalog.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {**catalog.public_product(product), "offers": product["offers"]}


@router.get("/categories")
def list_categories():
    return {"categories": catalog.categories()}


@router.get("/platforms")
def list_platforms():
    return {"platforms": [asdict(p) for p in catalog.load_platforms()]}
