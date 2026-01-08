from fastapi import APIRouter
import json
import os

router = APIRouter()

@router.get("/")
def get_products(item: str):
    file_path = os.path.join("data", "prices.json")

    with open(file_path, "r") as f:
        data = json.load(f)

    products = data.get(item.lower(), [])

    # calculate total for frontend
    for p in products:
        p["total"] = p["price"] + p["delivery"] + p["fee"]

    return products
