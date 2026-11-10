import httpx
import pytest
from fastapi.testclient import TestClient

from ai import explanation
from backend import catalog
from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["llm_explanations"] is False


def test_catalog_is_well_formed():
    platform_ids = {p.id for p in catalog.load_platforms()}
    ids = [p["id"] for p in catalog.load_products()]
    assert len(ids) == len(set(ids)) >= 40
    for product in catalog.load_products():
        assert set(product["offers"]) == platform_ids
        assert any(o["in_stock"] for o in product["offers"].values())
        assert all(o["price"] <= o["mrp"] for o in product["offers"].values())


def test_search_by_alias_and_typo():
    assert catalog.search("doodh")[0]["category"] == "Dairy"
    assert "Milk" in catalog.search("mlik")[0]["name"]
    assert catalog.search("zzzzzz") == []


def test_products_endpoint_filters():
    body = client.get("/products", params={"q": "rice"}).json()
    assert body["count"] >= 2
    assert all("rice" in p["name"].lower() for p in body["products"][:2])
    dairy = client.get("/products", params={"category": "Dairy", "limit": 100}).json()
    assert {p["category"] for p in dairy["products"]} == {"Dairy"}


def test_product_not_found():
    assert client.get("/products/nope").status_code == 404


def test_compare_ranks_offers_and_explains():
    body = client.get("/compare", params={"product_id": "butter-100g"}).json()
    offers = body["offers"]
    assert len(offers) == 3
    assert [o["score"] for o in offers] == sorted((o["score"] for o in offers), reverse=True)
    assert body["recommendation"]["recommended"] == offers[0]["platform"]
    assert offers[0]["platform"] in body["explanation"]["text"]
    assert body["explanation"]["source"] == "template"
    for o in offers:
        assert o["total"] == o["subtotal"] + sum(o["fees"].values())


def test_compare_cheapest_priority_picks_lowest_total():
    body = client.get(
        "/compare", params={"item": "atta", "priority": "cheapest", "qty": 2}
    ).json()
    assert body["offers"][0]["total"] == min(o["total"] for o in body["offers"])


def test_compare_lists_unavailable_platforms():
    body = client.get("/compare", params={"product_id": "milk-toned-1l"}).json()
    assert body["unavailable"] == ["Swiggy Instamart"]
    assert len(body["offers"]) == 2


def test_compare_validation():
    assert client.get("/compare").status_code == 422
    assert client.get("/compare", params={"item": "xyzxyz"}).status_code == 404
    assert client.get("/compare", params={"item": "milk", "qty": 0}).status_code == 422
    assert client.get("/compare", params={"item": "milk", "priority": "x"}).status_code == 422


def test_basket_merges_duplicates_and_ranks():
    payload = {
        "items": [
            {"product_id": "butter-100g", "qty": 1},
            {"product_id": "butter-100g", "qty": 1},
            {"product_id": "bread-white-400g", "qty": 1},
        ],
        "priority": "cheapest",
    }
    body = client.post("/basket", json=payload).json()
    assert len(body["platforms"]) == 3
    top = body["platforms"][0]
    butter = next(i for i in top["items"] if i["product_id"] == "butter-100g")
    assert butter["qty"] == 2
    assert top["total"] == min(p["total"] for p in body["platforms"])


def test_basket_reports_incomplete_platforms():
    payload = {"items": [{"product_id": "milk-toned-1l"}, {"product_id": "toothpaste-150g"}]}
    body = client.post("/basket", json=payload).json()
    assert [p["platform"] for p in body["platforms"]] == ["Blinkit"]
    assert {p["platform"] for p in body["incomplete"]} == {"Zepto", "Swiggy Instamart"}


def test_basket_validation():
    assert client.post("/basket", json={"items": []}).status_code == 422
    assert client.post("/basket", json={"items": [{"product_id": "nope"}]}).status_code == 404


def _fake_gemini(text):
    def fake_post(url, **kwargs):
        assert kwargs["headers"]["x-goog-api-key"] == "test-key"
        payload = {"candidates": [{"content": {"parts": [{"text": text}]}}]}
        return httpx.Response(200, json=payload, request=httpx.Request("POST", url))

    return fake_post


def test_llm_explanation_used_when_key_is_set(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    best = client.get("/compare", params={"product_id": "butter-100g"}).json()["offers"][0]
    monkeypatch.setattr(httpx, "post", _fake_gemini(f"{best['platform']} is the best choice."))
    body = client.get("/compare", params={"product_id": "butter-100g", "explain": "llm"}).json()
    assert body["explanation"] == {
        "text": f"{best['platform']} is the best choice.",
        "source": "llm",
    }


def test_llm_text_about_the_wrong_platform_is_rejected(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", _fake_gemini("Buy it from SomeOtherShop."))
    body = client.get("/compare", params={"product_id": "butter-100g", "explain": "llm"}).json()
    assert body["explanation"]["source"] == "template"


def test_llm_failure_falls_back_to_template(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def boom(url, **kwargs):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(httpx, "post", boom)
    body = client.get("/compare", params={"product_id": "butter-100g", "explain": "llm"}).json()
    assert body["explanation"]["source"] == "template"


def test_template_explanation_when_nothing_in_stock():
    text = explanation.template_explanation(None, "balanced", "1 x Thing")
    assert "in stock" in text
