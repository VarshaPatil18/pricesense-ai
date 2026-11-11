"""Generate the demo catalog used by PriceSense AI.

The output is SAMPLE DATA. Prices are derived from a rough MRP for each item
plus a seeded random discount per platform, so they are plausible but are not
the real prices on any platform. Re-running this script with the same seed
produces the same file.

Usage (from the repo root):
    python scripts/build_catalog.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

SEED = 2026
PLATFORMS = ["blinkit", "zepto", "instamart"]
OUT = Path(__file__).resolve().parent.parent / "backend" / "data" / "catalog.json"

# (id, name, brand, category, size value, size unit, rough MRP in rupees, aliases)
ITEMS = [
    ("milk-toned-1l", "Toned Milk", "Amul Taaza", "Dairy", 1000, "ml", 58, ["milk", "doodh"]),
    ("milk-full-cream-500ml", "Full Cream Milk", "Amul Gold", "Dairy", 500, "ml", 35, ["milk", "full cream"]),
    ("curd-400g", "Curd", "Mother Dairy", "Dairy", 400, "g", 40, ["dahi", "yogurt", "yoghurt"]),
    ("butter-100g", "Butter", "Amul", "Dairy", 100, "g", 60, ["makhan"]),
    ("paneer-200g", "Paneer", "Amul", "Dairy", 200, "g", 95, ["cottage cheese"]),
    ("cheese-slices-200g", "Cheese Slices", "Britannia", "Dairy", 200, "g", 155, ["cheese"]),
    ("eggs-6", "Eggs", "Farm Fresh", "Dairy", 6, "pc", 54, ["egg", "anda"]),
    ("bread-white-400g", "White Bread", "Britannia", "Bakery", 400, "g", 45, ["bread", "loaf"]),
    ("bread-brown-400g", "Brown Bread", "Harvest Gold", "Bakery", 400, "g", 55, ["bread", "wheat bread"]),
    ("rice-basmati-1kg", "Basmati Rice", "India Gate", "Staples", 1000, "g", 165, ["rice", "chawal"]),
    ("rice-sona-masoori-5kg", "Sona Masoori Rice", "Daawat", "Staples", 5000, "g", 420, ["rice", "chawal"]),
    ("atta-5kg", "Whole Wheat Atta", "Aashirvaad", "Staples", 5000, "g", 265, ["atta", "flour", "wheat flour"]),
    ("sugar-1kg", "Sugar", "Madhur", "Staples", 1000, "g", 58, ["cheeni", "shakkar"]),
    ("salt-1kg", "Iodised Salt", "Tata", "Staples", 1000, "g", 28, ["salt", "namak"]),
    ("toor-dal-1kg", "Toor Dal", "Tata Sampann", "Staples", 1000, "g", 199, ["dal", "arhar", "lentils"]),
    ("moong-dal-500g", "Moong Dal", "Tata Sampann", "Staples", 500, "g", 92, ["dal", "lentils"]),
    ("sunflower-oil-1l", "Sunflower Oil", "Fortune", "Staples", 1000, "ml", 165, ["oil", "cooking oil"]),
    ("mustard-oil-1l", "Mustard Oil", "Fortune", "Staples", 1000, "ml", 185, ["oil", "sarson"]),
    ("ghee-500ml", "Ghee", "Amul", "Staples", 500, "ml", 335, ["clarified butter"]),
    ("poha-500g", "Poha", "Tata Sampann", "Staples", 500, "g", 55, ["flattened rice", "chivda"]),
    ("tea-250g", "Tea", "Tata Tea Gold", "Beverages", 250, "g", 170, ["chai", "chai patti"]),
    ("coffee-50g", "Instant Coffee", "Nescafe Classic", "Beverages", 50, "g", 185, ["coffee"]),
    ("cola-750ml", "Cola", "Coca-Cola", "Beverages", 750, "ml", 45, ["coke", "soft drink", "cold drink"]),
    ("orange-juice-1l", "Orange Juice", "Real", "Beverages", 1000, "ml", 125, ["juice"]),
    ("water-1l", "Packaged Drinking Water", "Bisleri", "Beverages", 1000, "ml", 20, ["water", "paani"]),
    ("maggi-4pack", "Instant Noodles (Pack of 4)", "Maggi", "Snacks", 280, "g", 56, ["maggi", "noodles"]),
    ("biscuits-marie-250g", "Marie Biscuits", "Britannia", "Snacks", 250, "g", 40, ["biscuit", "cookies"]),
    ("chips-90g", "Potato Chips", "Lays", "Snacks", 90, "g", 50, ["chips", "crisps", "wafers"]),
    ("chocolate-50g", "Milk Chocolate", "Cadbury Dairy Milk", "Snacks", 50, "g", 45, ["chocolate", "dairy milk"]),
    ("peanut-butter-340g", "Peanut Butter", "Pintola", "Snacks", 340, "g", 199, ["pb"]),
    ("banana-6", "Banana", "Fresh", "Fruits & Vegetables", 6, "pc", 42, ["bananas", "kela"]),
    ("apple-4", "Apple", "Fresh", "Fruits & Vegetables", 4, "pc", 135, ["apples", "seb"]),
    ("tomato-500g", "Tomato", "Fresh", "Fruits & Vegetables", 500, "g", 28, ["tomatoes", "tamatar"]),
    ("onion-1kg", "Onion", "Fresh", "Fruits & Vegetables", 1000, "g", 42, ["onions", "pyaaz"]),
    ("potato-1kg", "Potato", "Fresh", "Fruits & Vegetables", 1000, "g", 38, ["potatoes", "aloo"]),
    ("coriander-100g", "Coriander Leaves", "Fresh", "Fruits & Vegetables", 100, "g", 15, ["dhaniya", "cilantro"]),
    ("dish-soap-500ml", "Dishwash Liquid", "Vim", "Household", 500, "ml", 115, ["dish soap", "vim"]),
    ("detergent-1kg", "Detergent Powder", "Surf Excel", "Household", 1000, "g", 145, ["washing powder", "surf"]),
    ("toilet-cleaner-500ml", "Toilet Cleaner", "Harpic", "Household", 500, "ml", 99, ["harpic"]),
    ("bath-soap-4pack", "Bath Soap (Pack of 4)", "Dove", "Personal Care", 400, "g", 240, ["soap"]),
    ("toothpaste-150g", "Toothpaste", "Colgate", "Personal Care", 150, "g", 110, ["colgate", "paste"]),
    ("shampoo-180ml", "Shampoo", "Head & Shoulders", "Personal Care", 180, "ml", 175, ["hair wash"]),
]


def build() -> list[dict]:
    rng = random.Random(SEED)
    products = []
    for pid, name, brand, category, size, unit, mrp, aliases in ITEMS:
        # Roughly one product in eight is missing from one platform.
        missing = rng.choice(PLATFORMS) if rng.random() < 0.125 else None
        offers = {}
        for platform in PLATFORMS:
            discount = rng.uniform(0.0, 0.14)
            price = max(1, round(mrp * (1 - discount)))
            offers[platform] = {
                "price": price,
                "mrp": mrp,
                "in_stock": platform != missing,
            }
        products.append(
            {
                "id": pid,
                "name": name,
                "brand": brand,
                "category": category,
                "size": {"value": size, "unit": unit},
                "aliases": aliases,
                "offers": offers,
            }
        )
    return products


if __name__ == "__main__":
    data = {
        "note": "Sample data for demonstration. Not real platform prices.",
        "seed": SEED,
        "products": build(),
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(data['products'])} products to {OUT}")
