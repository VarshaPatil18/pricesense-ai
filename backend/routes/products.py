from fastapi import APIRouter
import json
import os

router = APIRouter()

DATA_PATH = os.path.join("data", "prices.json")

@router.get("/")
def get_products(item: str = "milk"):
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    return data.get(item.lower(), [])
