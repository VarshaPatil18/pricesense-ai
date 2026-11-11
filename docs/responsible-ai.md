# Responsible AI notes

## Transparency

- Every recommendation comes with the full fee breakdown and the score for each platform, so a shopper can check the reasoning rather than trust it.
- The explanation states the trade-off, including when another platform is cheaper or faster than the recommended one.
- The UI labels each explanation as rule-based or written by Gemini.
- The app and the API both state that the data is sample data.

## Reliability

- The platform is chosen by a deterministic scoring engine, not by a language model. The same input always gives the same recommendation, and the logic is unit tested.
- When LLM explanations are enabled, the model receives only the computed facts and is instructed not to add prices, offers or platforms. Its reply is discarded if the call fails, times out, or does not mention the recommended platform, and the rule-based explanation is used instead.
- A known gap: the grounding check confirms the platform name but does not verify every number in the model's text. A stricter check would compare each rupee amount in the reply against the facts.

## Fairness

- No platform is favoured. Ranking uses only total cost and delivery time. Ties are broken by cost, then time, then name.
- There are no sponsored placements or affiliate links.
- The fee rules and prices here are illustrative. Presenting them as real would be unfair to the platforms, which is why the demo label is prominent.

## Privacy

- There are no accounts and nothing is stored. Basket contents live in the browser's memory and are sent to the API only to compute a comparison.
- When LLM explanations are enabled, the product names, prices and totals for the current comparison are sent to Google's Gemini API. No personal information is included.
- API keys are read from the environment and `.env` is git-ignored.

## Limits a user should know

- Prices, stock, fees and delivery times are not live.
- The "balanced" setting values a minute of waiting at ₹2. That is a default, not a fact about any individual shopper.
- The split-order suggestion is a heuristic and may not be the cheapest possible split.
