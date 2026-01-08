from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def recommend_best(products: list[dict]):
    if not products:
        return {"message": "No products found"}

    best = min(products, key=lambda x: x["total"])
    return {
        "recommended_platform": best["platform"],
        "reason": "Lowest total price"
    }
