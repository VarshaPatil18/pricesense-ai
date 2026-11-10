"""Scoring engine: turns prices, fees and delivery times into a ranked list.

Everything here is pure Python with no I/O, so it is easy to test and the
result for a given input is always the same.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

# How each shopper priority turns an option into a single "effective cost"
# (lower is better):
#   cheapest - the all-in total, in rupees
#   fastest  - the delivery time, in minutes
#   balanced - the total plus a rupee value for every minute of waiting
PRIORITIES = ("cheapest", "balanced", "fastest")
DEFAULT_PRIORITY = "balanced"
RUPEES_PER_MINUTE = 2.0
# A split order means two deliveries, so only suggest it for a real saving.
MIN_SPLIT_SAVING = 10


@dataclass(frozen=True)
class Platform:
    id: str
    name: str
    delivery_fee: int
    free_delivery_above: int
    handling_fee: int
    small_cart_fee: int
    small_cart_below: int
    eta_minutes: int


@dataclass(frozen=True)
class Line:
    """One basket line: a product and how many of it."""

    product: dict
    qty: int


def cart_fees(platform: Platform, subtotal: int) -> dict[str, int]:
    """Fees a platform adds to a cart with the given item subtotal."""
    if subtotal <= 0:
        return {"delivery": 0, "handling": 0, "small_cart": 0}
    delivery = 0 if subtotal >= platform.free_delivery_above else platform.delivery_fee
    small_cart = platform.small_cart_fee if subtotal < platform.small_cart_below else 0
    return {"delivery": delivery, "handling": platform.handling_fee, "small_cart": small_cart}


def quote(platform: Platform, lines: list[Line]) -> dict:
    """Price a set of lines on one platform, noting anything it cannot supply."""
    items, missing, subtotal = [], [], 0
    for line in lines:
        offer = line.product["offers"].get(platform.id)
        if not offer or not offer.get("in_stock", False):
            missing.append(line.product["id"])
            continue
        line_total = offer["price"] * line.qty
        subtotal += line_total
        items.append(
            {
                "product_id": line.product["id"],
                "qty": line.qty,
                "unit_price": offer["price"],
                "mrp": offer["mrp"],
                "line_total": line_total,
            }
        )
    fees = cart_fees(platform, subtotal)
    return {
        "platform_id": platform.id,
        "platform": platform.name,
        "items": items,
        "missing": missing,
        "subtotal": subtotal,
        "fees": fees,
        "total": subtotal + sum(fees.values()),
        "eta_minutes": platform.eta_minutes,
    }


def effective_cost(option: dict, priority: str) -> float:
    if priority == "cheapest":
        return float(option["total"])
    if priority == "fastest":
        return float(option["eta_minutes"])
    return option["total"] + RUPEES_PER_MINUTE * option["eta_minutes"]


def rank(options: list[dict], priority: str = DEFAULT_PRIORITY) -> list[dict]:
    """Score options from 0 to 100 (higher is better) and sort best first.

    The best option scores 100. Every other option scores in proportion to how
    much worse its effective cost is, so an option that is twice as costly (or
    twice as slow, when the priority is "fastest") scores 50.
    """
    if priority not in PRIORITIES:
        raise ValueError(f"Unknown priority: {priority!r}")
    if not options:
        return []
    costs = [effective_cost(o, priority) for o in options]
    best = min(costs)
    scored = [
        {**option, "score": round(100 * best / cost, 1) if cost else 100.0}
        for option, cost in zip(options, costs)
    ]
    scored.sort(key=lambda o: (-o["score"], o["total"], o["eta_minutes"], o["platform"]))
    return scored


def compare_item(
    product: dict, qty: int, platforms: list[Platform], priority: str = DEFAULT_PRIORITY
) -> dict:
    """Rank the platforms for a single product."""
    quotes = [quote(p, [Line(product, qty)]) for p in platforms]
    available = [q for q in quotes if not q["missing"]]
    ranked = rank(available, priority)
    return {
        "ranked": ranked,
        "unavailable": [q["platform"] for q in quotes if q["missing"]],
        "summary": _summary(ranked),
    }


def compare_basket(
    lines: list[Line], platforms: list[Platform], priority: str = DEFAULT_PRIORITY
) -> dict:
    """Rank platforms for a whole basket and look for a cheaper split order."""
    quotes = [quote(p, lines) for p in platforms]
    complete = [q for q in quotes if not q["missing"]]
    ranked = rank(complete, priority)
    return {
        "ranked": ranked,
        "incomplete": [q for q in quotes if q["missing"]],
        "split": best_split(lines, platforms, ranked),
        "summary": _summary(ranked),
    }


def best_split(lines: list[Line], platforms: list[Platform], ranked: list[dict]) -> dict | None:
    """Find a cheaper way to buy the basket across two or more platforms.

    Heuristic: for every group of two or more platforms, send each item to
    whichever platform in the group sells it cheapest, then add each
    platform's fees. This ignores the chance that moving an item could tip a
    cart over a free-delivery threshold, so it is good but not guaranteed
    optimal. Returns None unless the split saves at least MIN_SPLIT_SAVING
    rupees over the cheapest single platform.
    """
    cheapest_single = min((q["total"] for q in ranked), default=None)
    best = None
    for size in range(2, len(platforms) + 1):
        for group in combinations(platforms, size):
            assignment: dict[str, list[Line]] = {p.id: [] for p in group}
            covered = True
            for line in lines:
                sellers = [
                    p
                    for p in group
                    if line.product["offers"].get(p.id, {}).get("in_stock", False)
                ]
                if not sellers:
                    covered = False
                    break
                pick = min(sellers, key=lambda p: line.product["offers"][p.id]["price"])
                assignment[pick.id].append(line)
            if not covered:
                continue
            orders = [quote(p, assignment[p.id]) for p in group if assignment[p.id]]
            if len(orders) < 2:
                continue
            total = sum(o["total"] for o in orders)
            if best is None or total < best["total"]:
                best = {
                    "orders": orders,
                    "total": total,
                    "eta_minutes": max(o["eta_minutes"] for o in orders),
                }
    if best is None:
        return None
    if cheapest_single is not None:
        if cheapest_single - best["total"] < MIN_SPLIT_SAVING:
            return None
        best["saves_vs_single"] = cheapest_single - best["total"]
    return best


def _summary(ranked: list[dict]) -> dict | None:
    """Headline facts about a ranking, used by the UI and the explanation."""
    if not ranked:
        return None
    top = ranked[0]
    cheapest = min(ranked, key=lambda o: (o["total"], o["eta_minutes"]))
    fastest = min(ranked, key=lambda o: (o["eta_minutes"], o["total"]))
    priciest = max(ranked, key=lambda o: o["total"])
    return {
        "recommended": top["platform"],
        "total": top["total"],
        "eta_minutes": top["eta_minutes"],
        "score": top["score"],
        "cheapest": cheapest["platform"],
        "cheapest_total": cheapest["total"],
        "fastest": fastest["platform"],
        "fastest_eta": fastest["eta_minutes"],
        "saves_vs_priciest": priciest["total"] - top["total"],
        "extra_vs_cheapest": top["total"] - cheapest["total"],
        "minutes_saved_vs_cheapest": cheapest["eta_minutes"] - top["eta_minutes"],
        "options_compared": len(ranked),
    }
