from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ai import explanation, scoring
from backend import catalog

router = APIRouter()

Priority = Literal["cheapest", "balanced", "fastest"]
Explain = Literal["template", "llm"]


class BasketItem(BaseModel):
    product_id: str = Field(max_length=60)
    qty: int = Field(1, ge=1, le=20)


class BasketRequest(BaseModel):
    items: list[BasketItem] = Field(min_length=1, max_length=30)
    priority: Priority = "balanced"
    explain: Explain = "template"


def _resolve(product_id: str | None, item: str | None) -> dict:
    if product_id:
        product = catalog.get_product(product_id)
    elif item:
        matches = catalog.search(item, limit=1)
        product = matches[0] if matches else None
    else:
        raise HTTPException(status_code=422, detail="Provide product_id or item")
    if not product:
        raise HTTPException(status_code=404, detail="No matching product in the catalog")
    return product


def _with_unit_price(option: dict, product: dict) -> dict:
    line = option["items"][0]
    return {**option, "unit_price_label": catalog.unit_price_label(product, line["unit_price"])}


@router.get("/compare")
def compare(
    product_id: str | None = Query(None, max_length=60),
    item: str | None = Query(None, max_length=60, description="Free-text search, e.g. 'milk'"),
    qty: int = Query(1, ge=1, le=20),
    priority: Priority = "balanced",
    explain: Explain = "template",
):
    """Compare one product across platforms and recommend where to buy it."""
    product = _resolve(product_id, item)
    result = scoring.compare_item(product, qty, list(catalog.load_platforms()), priority)
    subject = f"{qty} x {product['brand']} {product['name']} ({catalog.size_label(product)})"
    return {
        "product": catalog.public_product(product),
        "qty": qty,
        "priority": priority,
        "offers": [_with_unit_price(o, product) for o in result["ranked"]],
        "unavailable": result["unavailable"],
        "recommendation": result["summary"],
        "explanation": explanation.explain(
            result["summary"], priority, subject, result["ranked"], use_llm=explain == "llm"
        ),
        "demo_data": True,
    }


@router.post("/basket")
def basket(request: BasketRequest):
    """Compare a whole basket and check whether splitting the order is cheaper."""
    quantities: dict[str, int] = {}
    for entry in request.items:
        quantities[entry.product_id] = quantities.get(entry.product_id, 0) + entry.qty

    lines = []
    for product_id, qty in quantities.items():
        product = catalog.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Unknown product: {product_id}")
        lines.append(scoring.Line(product, min(qty, 20)))

    result = scoring.compare_basket(lines, list(catalog.load_platforms()), request.priority)
    count = sum(line.qty for line in lines)
    subject = f"this basket of {count} item{'s' if count != 1 else ''}"
    return {
        "priority": request.priority,
        "products": {l.product["id"]: catalog.public_product(l.product) for l in lines},
        "platforms": result["ranked"],
        "incomplete": result["incomplete"],
        "split": result["split"],
        "recommendation": result["summary"],
        "explanation": explanation.explain(
            result["summary"],
            request.priority,
            subject,
            result["ranked"],
            use_llm=request.explain == "llm",
        ),
        "demo_data": True,
    }
