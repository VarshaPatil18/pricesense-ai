import { useEffect, useState } from "react";
import Header from "./components/Header";
import Compare from "./pages/Compare";
import Basket from "./pages/Basket";
import { getHealth } from "./utils/api";
import "./styles.css";

const TABS = [
  { id: "compare", label: "Compare an item" },
  { id: "basket", label: "Compare a basket" },
];

export default function App() {
  const [tab, setTab] = useState("compare");
  const [priority, setPriority] = useState("balanced");
  const [basket, setBasket] = useState([]);
  const [llm, setLlm] = useState(false);

  useEffect(() => {
    getHealth()
      .then((health) => setLlm(health.llm_explanations))
      .catch(() => setLlm(false));
  }, []);

  function addToBasket(product) {
    setBasket((items) => {
      const existing = items.find((i) => i.product.id === product.id);
      if (existing) {
        return items.map((i) =>
          i.product.id === product.id ? { ...i, qty: Math.min(i.qty + 1, 20) } : i
        );
      }
      return [...items, { product, qty: 1 }];
    });
  }

  const explain = llm ? "llm" : "template";
  const count = basket.reduce((sum, i) => sum + i.qty, 0);

  return (
    <div className="container">
      <Header />
      <nav className="tabs" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={tab === t.id ? "tab active" : "tab"}
            onClick={() => setTab(t.id)}
          >
            {t.label}
            {t.id === "basket" && count > 0 ? <span className="count">{count}</span> : null}
          </button>
        ))}
      </nav>

      {tab === "compare" ? (
        <Compare
          priority={priority}
          onPriority={setPriority}
          explain={explain}
          onAddToBasket={addToBasket}
        />
      ) : (
        <Basket
          basket={basket}
          setBasket={setBasket}
          onAdd={addToBasket}
          priority={priority}
          onPriority={setPriority}
          explain={explain}
        />
      )}

      <footer className="footer">
        Prices and fees are sample data for demonstration, not live prices from any platform.
      </footer>
    </div>
  );
}
