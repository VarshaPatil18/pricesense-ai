from fastapi import APIRouter
import json
import os

router = APIRouter()

@router.get("/")
def recommend(item: str):
    file_path = os.path.join("data", "prices.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    products = data.get(item.lower(), [])
    if not products:
        return {"message": "No data available"}

    # AI logic (prototype-friendly)
    best = min(
        products,
        key=lambda x: (x["price"] + x["delivery"] + x["fee"], x["eta"])
    )

    return {
        "platform": best["platform"],
        "total": best["price"] + best["delivery"] + best["fee"],
        "eta": best["eta"],
        "reason": (
            f"{best['platform']} offers the lowest total price "
            f"with delivery in {best['eta']} mins."
        )
    }
