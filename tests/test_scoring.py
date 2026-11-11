import pytest

from ai import scoring
from ai.scoring import Line, Platform

FAST = Platform("fast", "Fast", 30, 150, 5, 15, 99, 9)
CHEAP = Platform("cheap", "Cheap", 25, 200, 4, 20, 99, 20)
PLATFORMS = [FAST, CHEAP]


def product(pid, fast=None, cheap=None):
    def offer(price):
        return {"price": price or 0, "mrp": price or 0, "in_stock": price is not None}

    return {"id": pid, "offers": {"fast": offer(fast), "cheap": offer(cheap)}}


def test_cart_fees_below_thresholds():
    assert scoring.cart_fees(FAST, 50) == {"delivery": 30, "handling": 5, "small_cart": 15}


def test_cart_fees_free_delivery_at_threshold():
    assert scoring.cart_fees(FAST, 150) == {"delivery": 0, "handling": 5, "small_cart": 0}


def test_cart_fees_empty_cart_costs_nothing():
    assert scoring.cart_fees(FAST, 0) == {"delivery": 0, "handling": 0, "small_cart": 0}


def test_quote_totals_and_missing_items():
    lines = [Line(product("a", fast=60, cheap=55), 2), Line(product("b", fast=None, cheap=40), 1)]
    q = scoring.quote(FAST, lines)
    assert q["subtotal"] == 120
    assert q["missing"] == ["b"]
    assert q["total"] == 120 + 30 + 5  # delivery + handling, above small-cart limit


def test_priority_changes_the_winner():
    options = [
        {"platform": "Fast", "total": 120, "eta_minutes": 9},
        {"platform": "Cheap", "total": 100, "eta_minutes": 20},
    ]
    assert scoring.rank(options, "cheapest")[0]["platform"] == "Cheap"
    assert scoring.rank(options, "fastest")[0]["platform"] == "Fast"


def test_cheapest_and_fastest_are_strict():
    options = [
        {"platform": "Fast", "total": 101, "eta_minutes": 9},
        {"platform": "Cheap", "total": 100, "eta_minutes": 60},
    ]
    assert scoring.rank(options, "cheapest")[0]["platform"] == "Cheap"
    assert scoring.rank(options, "fastest")[0]["platform"] == "Fast"


def test_balanced_weighs_the_size_of_the_difference():
    # Rs 1 cheaper is not worth 51 extra minutes...
    small_saving = [
        {"platform": "Fast", "total": 101, "eta_minutes": 9},
        {"platform": "Cheap", "total": 100, "eta_minutes": 60},
    ]
    assert scoring.rank(small_saving, "balanced")[0]["platform"] == "Fast"
    # ...but Rs 150 cheaper is.
    big_saving = [
        {"platform": "Fast", "total": 250, "eta_minutes": 9},
        {"platform": "Cheap", "total": 100, "eta_minutes": 60},
    ]
    assert scoring.rank(big_saving, "balanced")[0]["platform"] == "Cheap"


def test_rank_scores_are_proportional():
    options = [
        {"platform": "A", "total": 100, "eta_minutes": 10},
        {"platform": "B", "total": 200, "eta_minutes": 10},
    ]
    ranked = scoring.rank(options, "cheapest")
    assert [o["score"] for o in ranked] == [100.0, 50.0]


def test_rank_handles_identical_options():
    options = [
        {"platform": "B", "total": 100, "eta_minutes": 10},
        {"platform": "A", "total": 100, "eta_minutes": 10},
    ]
    ranked = scoring.rank(options)
    assert [o["platform"] for o in ranked] == ["A", "B"]
    assert all(o["score"] == 100.0 for o in ranked)


def test_rank_rejects_unknown_priority():
    with pytest.raises(ValueError):
        scoring.rank([{"platform": "A", "total": 1, "eta_minutes": 1}], "whatever")


def test_compare_item_excludes_out_of_stock_platforms():
    result = scoring.compare_item(product("a", fast=60, cheap=None), 1, PLATFORMS)
    assert [o["platform"] for o in result["ranked"]] == ["Fast"]
    assert result["unavailable"] == ["Cheap"]
    assert result["summary"]["options_compared"] == 1


def test_compare_item_with_no_stock_anywhere():
    result = scoring.compare_item(product("a"), 1, PLATFORMS)
    assert result["ranked"] == []
    assert result["summary"] is None


def test_summary_reports_tradeoff():
    result = scoring.compare_item(product("a", fast=60, cheap=40), 1, PLATFORMS, "fastest")
    s = result["summary"]
    assert s["recommended"] == "Fast"
    assert s["cheapest"] == "Cheap"
    assert s["extra_vs_cheapest"] == (60 + 30 + 5 + 15) - (40 + 25 + 4 + 20)
    assert s["minutes_saved_vs_cheapest"] == 11


def test_split_found_when_it_beats_single_platform():
    # Each platform is much cheaper on one item and both carts get free delivery.
    lines = [
        Line(product("a", fast=200, cheap=400), 1),
        Line(product("b", fast=400, cheap=200), 1),
    ]
    result = scoring.compare_basket(lines, PLATFORMS, "cheapest")
    split = result["split"]
    assert split is not None
    assert split["total"] == (200 + 5) + (200 + 4)
    assert split["saves_vs_single"] == min(o["total"] for o in result["ranked"]) - split["total"]
    assert split["eta_minutes"] == 20


def test_no_split_when_fees_outweigh_savings():
    lines = [
        Line(product("a", fast=50, cheap=52), 1),
        Line(product("b", fast=52, cheap=50), 1),
    ]
    assert scoring.compare_basket(lines, PLATFORMS)["split"] is None


def test_split_offered_when_no_single_platform_has_everything():
    lines = [
        Line(product("a", fast=50, cheap=None), 1),
        Line(product("b", fast=None, cheap=50), 1),
    ]
    result = scoring.compare_basket(lines, PLATFORMS)
    assert result["ranked"] == []
    assert len(result["incomplete"]) == 2
    assert result["split"] is not None
    assert "saves_vs_single" not in result["split"]
