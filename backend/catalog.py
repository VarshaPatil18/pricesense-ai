"""Loads the sample catalog and platform fee rules, and searches products."""

from __future__ import annotations

import json
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

from ai.scoring import Platform

DATA_DIR = Path(__file__).resolve().parent / "data"
FUZZY_THRESHOLD = 0.75


@lru_cache(maxsize=1)
def load_products() -> tuple[dict, ...]:
    data = json.loads((DATA_DIR / "catalog.json").read_text(encoding="utf-8"))
    return tuple(data["products"])


@lru_cache(maxsize=1)
def load_platforms() -> tuple[Platform, ...]:
    data = json.loads((DATA_DIR / "platforms.json").read_text(encoding="utf-8"))
    return tuple(Platform(**p) for p in data["platforms"])


def get_product(product_id: str) -> dict | None:
    return next((p for p in load_products() if p["id"] == product_id), None)


def categories() -> list[str]:
    return sorted({p["category"] for p in load_products()})


def _match_score(query: str, product: dict) -> float:
    """How well a product matches a query, from 0 (no match) to 1 (exact)."""
    name = product["name"].lower()
    brand = product["brand"].lower()
    aliases = [a.lower() for a in product["aliases"]]
    terms = [name, brand, *aliases]

    if query == name or query in aliases:
        return 1.0
    if any(t.startswith(query) for t in terms):
        return 0.9
    if any(query in t for t in terms) or query in f"{brand} {name}":
        return 0.8
    # Typos: compare against each word and each whole term.
    words = {w for t in terms for w in t.split()} | set(terms)
    best = max((SequenceMatcher(None, query, w).ratio() for w in words), default=0.0)
    return best * 0.7 if best >= FUZZY_THRESHOLD else 0.0


def search(query: str = "", category: str | None = None, limit: int = 20) -> list[dict]:
    """Search by name, brand or alias. An empty query lists the catalog."""
    products = list(load_products())
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    query = query.strip().lower()
    if not query:
        return products[:limit]
    scored = [(s, p) for p in products if (s := _match_score(query, p)) > 0]
    scored.sort(key=lambda sp: (-sp[0], sp[1]["name"]))
    return [p for _, p in scored[:limit]]


def unit_price_label(product: dict, price: int) -> str | None:
    """Price per 100 g / 100 ml / piece, for comparing pack sizes."""
    value, unit = product["size"]["value"], product["size"]["unit"]
    if not value:
        return None
    if unit == "pc":
        return f"₹{price / value:.2f} per piece"
    return f"₹{price / value * 100:.2f} per 100 {unit}"


def size_label(product: dict) -> str:
    value, unit = product["size"]["value"], product["size"]["unit"]
    if unit == "pc":
        return f"{value} pc"
    if value >= 1000:
        big = value / 1000
        return f"{big:g} {'kg' if unit == 'g' else 'L'}"
    return f"{value} {unit}"


def public_product(product: dict) -> dict:
    """Product shape returned by the API."""
    prices = [o["price"] for o in product["offers"].values() if o["in_stock"]]
    return {
        "id": product["id"],
        "name": product["name"],
        "brand": product["brand"],
        "category": product["category"],
        "size": size_label(product),
        "from_price": min(prices) if prices else None,
        "platforms_in_stock": len(prices),
    }
