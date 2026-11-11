import { useEffect, useState } from "react";
import SearchBar from "../components/SearchBar";
import PrioritySelector from "../components/PrioritySelector";
import Recommendation from "../components/Recommendation";
import PriceTable from "../components/PriceTable";
import { compareBasket } from "../utils/api";
import { rupees } from "../utils/format";

export default function Basket({ basket, setBasket, onAdd, priority, onPriority, explain }) {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const key = basket.map((i) => `${i.product.id}:${i.qty}`).join(",");

  useEffect(() => {
    if (basket.length === 0) {
      setResult(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    const items = basket.map((i) => ({ product_id: i.product.id, qty: i.qty }));
    compareBasket({ items, priority, explain })
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
    // `key` captures the basket contents.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, priority, explain]);

  function setQty(id, qty) {
    setBasket((items) =>
      qty < 1
        ? items.filter((i) => i.product.id !== id)
        : items.map((i) => (i.product.id === id ? { ...i, qty: Math.min(qty, 20) } : i))
    );
  }

  const name = (id) => result?.products[id]?.name ?? id;

  return (
    <section>
      <div className="card">
        <SearchBar onSelect={onAdd} placeholder="Add an item to your basket…" />
        {basket.length === 0 ? (
          <p className="muted center">
            Your basket is empty. Add a few items to see which platform is best for the whole order.
          </p>
        ) : (
          <ul className="basket-list">
            {basket.map(({ product, qty }) => (
              <li key={product.id}>
                <span>
                  <strong>{product.name}</strong>
                  <span className="muted">
                    {" "}
                    · {product.brand} · {product.size}
                  </span>
                </span>
                <div className="qty">
                  <button
                    aria-label={`Decrease ${product.name}`}
                    onClick={() => setQty(product.id, qty - 1)}
                  >
                    −
                  </button>
                  <span>{qty}</span>
                  <button
                    aria-label={`Increase ${product.name}`}
                    onClick={() => setQty(product.id, qty + 1)}
                  >
                    +
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {result && basket.length > 0 && (
        <div className={loading ? "results loading" : "results"}>
          <PrioritySelector value={priority} onChange={onPriority} />
          <Recommendation recommendation={result.recommendation} explanation={result.explanation} />
          <PriceTable offers={result.platforms} />

          {result.incomplete.map((p) => (
            <p key={p.platform_id} className="muted">
              {p.platform} is missing {p.missing.map(name).join(", ")}.
            </p>
          ))}

          {result.split && (
            <div className="split">
              <span className="eyebrow">Split order</span>
              <h3>
                {result.split.saves_vs_single
                  ? `Save ${rupees(result.split.saves_vs_single)} by splitting the order across ${
                      result.split.orders.length
                    } platforms`
                  : "No single platform has everything, so split the order"}
              </h3>
              <ul>
                {result.split.orders.map((o) => (
                  <li key={o.platform_id}>
                    <strong>{o.platform}</strong> ({rupees(o.total)}):{" "}
                    {o.items.map((i) => `${i.qty} × ${name(i.product_id)}`).join(", ")}
                  </li>
                ))}
              </ul>
              <p className="muted">
                {rupees(result.split.total)} in total, everything delivered within{" "}
                {result.split.eta_minutes} minutes.
              </p>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
