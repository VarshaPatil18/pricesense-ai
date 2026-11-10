import { rupees } from "../utils/format";

export default function Recommendation({ recommendation, explanation }) {
  if (!recommendation) {
    return (
      <div className="recommendation empty">
        <p>{explanation.text}</p>
      </div>
    );
  }
  return (
    <div className="recommendation">
      <div className="rec-head">
        <div>
          <span className="eyebrow">Recommended</span>
          <h2>{recommendation.recommended}</h2>
        </div>
        <div className="rec-stats">
          <div>
            <strong>{rupees(recommendation.total)}</strong>
            <span>all-in</span>
          </div>
          <div>
            <strong>{recommendation.eta_minutes} min</strong>
            <span>delivery</span>
          </div>
        </div>
      </div>
      <p>{explanation.text}</p>
      <span className="source">
        {explanation.source === "llm" ? "Explanation written by Gemini" : "Rule-based explanation"}
      </span>
    </div>
  );
}
