import { useEffect, useState } from "react";
import SearchBar from "../components/SearchBar";
import PrioritySelector from "../components/PrioritySelector";
import Recommendation from "../components/Recommendation";
import PriceTable from "../components/PriceTable";
import { compareProduct } from "../utils/api";

const STARTERS = [
  { id: "butter-100g", label: "Butter" },
  { id: "atta-5kg", label: "Atta 5 kg" },
  { id: "maggi-4pack", label: "Maggi" },
  { id: "eggs-6", label: "Eggs" },
];

export default function Compare({ priority, onPriority, explain, onAddToBasket }) {
  const [productId, setProductId] = useState(null);
  const [qty, setQty] = useState(1);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;
    setLoading(true);
    compareProduct({ productId, qty, priority, explain })
      .then((data) => {
        if (cancelled) return;
        setResult(data);
        setError("");
      })
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [productId, qty, priority, explain]);

  function select(id) {
    setProductId(id);
    setQty(1);
    setAdded(false);
  }

  return (
    <section>
      <div className="card">
        <SearchBar onSelect={(p) => select(p.id)} />
        {!result && (
          <div className="starters">
            <span className="muted">Try:</span>
            {STARTERS.map((s) => (
              <button key={s.id} className="chip" onClick={() => select(s.id)}>
                {s.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className={loading ? "results loading" : "results"}>
          <div className="result-head">
            <div>
              <h2>
                {result.product.brand} {result.product.name}
              </h2>
              <span className="muted">
                {result.product.size} · {result.product.category}
              </span>
            </div>
            <div className="qty">
              <button aria-label="Decrease quantity" onClick={() => setQty(Math.max(1, qty - 1))}>
                −
              </button>
              <span aria-live="polite">{qty}</span>
              <button aria-label="Increase quantity" onClick={() => setQty(Math.min(20, qty + 1))}>
                +
              </button>
            </div>
          </div>

          <PrioritySelector value={priority} onChange={onPriority} />
          <Recommendation recommendation={result.recommendation} explanation={result.explanation} />
          <PriceTable offers={result.offers} showUnitPrice />

          {result.unavailable.length > 0 && (
            <p className="muted">Out of stock on {result.unavailable.join(", ")}.</p>
          )}

          <button
            className="secondary"
            onClick={() => {
              onAddToBasket(result.product);
              setAdded(true);
            }}
          >
            {added ? "Added to basket" : "Add to basket"}
          </button>
        </div>
      )}
    </section>
  );
}
