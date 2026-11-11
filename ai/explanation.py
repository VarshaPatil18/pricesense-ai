"""Explanations for a recommendation.

There are two writers:

* ``template_explanation`` builds the text from the computed numbers. It needs
  no network and always works.
* ``llm_explanation`` asks Gemini to phrase the same numbers more naturally.
  It only runs when GEMINI_API_KEY is set, and any failure falls back to the
  template.

The model never chooses the platform. The scoring engine has already decided;
the model is given those facts and asked to explain them.
"""

from __future__ import annotations

import json
import os

import httpx

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-2.5-flash"
TIMEOUT_SECONDS = 8.0
MAX_CHARS = 600

PRIORITY_PHRASE = {
    "cheapest": "you asked for the lowest price",
    "balanced": "you asked for a balance of price and speed",
    "fastest": "you asked for the fastest delivery",
}

PROMPT = """You explain grocery price comparisons to a shopper in India.
Using ONLY the facts in the JSON below, write 2 short sentences explaining why
"{platform}" is recommended. Mention the total in rupees and the delivery time.
If another platform is cheaper or faster, say so honestly and give the trade-off.
Do not invent prices, offers, discounts or platforms. Plain text only.

FACTS:
{facts}
"""


def llm_available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def template_explanation(summary: dict | None, priority: str, subject: str) -> str:
    """Deterministic explanation built from the scoring summary."""
    if not summary:
        return f"None of the platforms currently has {subject} in stock."

    name = summary["recommended"]
    parts = [
        f"{name} is the best pick for {subject}: ₹{summary['total']} all-in, "
        f"delivered in about {summary['eta_minutes']} minutes."
    ]
    if summary["options_compared"] == 1:
        parts.append("It is the only platform that has everything in stock.")
        return " ".join(parts)

    reason = PRIORITY_PHRASE.get(priority, PRIORITY_PHRASE["balanced"])
    if summary["extra_vs_cheapest"] > 0:
        parts.append(
            f"{summary['cheapest']} is ₹{summary['extra_vs_cheapest']} cheaper, but "
            f"{name} arrives {summary['minutes_saved_vs_cheapest']} minutes sooner and {reason}."
        )
    elif summary["fastest"] != name:
        wait = summary["eta_minutes"] - summary["fastest_eta"]
        parts.append(
            f"It is the cheapest option. {summary['fastest']} is {wait} minutes faster "
            f"but costs more, and {reason}."
        )
    else:
        parts.append("It is both the cheapest and the fastest option.")
    if summary["saves_vs_priciest"] > 0:
        parts.append(
            f"You save ₹{summary['saves_vs_priciest']} compared with the most expensive platform."
        )
    return " ".join(parts)


def llm_explanation(facts: dict, platform: str) -> str | None:
    """Ask Gemini to phrase the facts. Returns None on any problem."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    prompt = PROMPT.format(platform=platform, facts=json.dumps(facts, indent=2))
    try:
        response = httpx.post(
            GEMINI_URL.format(model=model),
            headers={"x-goog-api-key": api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return None
    # Grounding check: the text must be about the platform the engine chose.
    if not text or platform.lower() not in text.lower():
        return None
    return text[:MAX_CHARS]


def explain(
    summary: dict | None,
    priority: str,
    subject: str,
    options: list[dict] | None = None,
    use_llm: bool = False,
) -> dict:
    """Return ``{"text": ..., "source": "llm" | "template"}``."""
    if use_llm and summary:
        facts = {
            "shopping_for": subject,
            "priority": priority,
            "summary": summary,
            "options": [
                {
                    "platform": o["platform"],
                    "total": o["total"],
                    "eta_minutes": o["eta_minutes"],
                    "score": o["score"],
                }
                for o in (options or [])
            ],
        }
        text = llm_explanation(facts, summary["recommended"])
        if text:
            return {"text": text, "source": "llm"}
    return {"text": template_explanation(summary, priority, subject), "source": "template"}
