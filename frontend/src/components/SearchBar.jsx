import { useEffect, useRef, useState } from "react";
import { searchProducts } from "../utils/api";
import { rupees } from "../utils/format";

export default function SearchBar({ onSelect, placeholder = "Search milk, rice, atta…" }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const latest = useRef(0);

  useEffect(() => {
    const q = query.trim();
    if (!q) {
      setResults([]);
      return;
    }
    const id = ++latest.current;
    const timer = setTimeout(() => {
      searchProducts(q)
        .then((data) => {
          if (id !== latest.current) return;
          setResults(data.products);
          setError("");
        })
        .catch((e) => id === latest.current && setError(e.message));
    }, 200);
    return () => clearTimeout(timer);
  }, [query]);

  function choose(product) {
    onSelect(product);
    setQuery("");
    setResults([]);
    setOpen(false);
  }

  const showList = open && query.trim() !== "";

  return (
    <div className="search">
      <input
        type="search"
        value={query}
        placeholder={placeholder}
        aria-label="Search products"
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && results.length > 0) choose(results[0]);
          if (e.key === "Escape") setOpen(false);
        }}
      />
      {showList && (
        <ul className="suggestions">
          {error && <li className="muted">{error}</li>}
          {!error && results.length === 0 && <li className="muted">No matching products</li>}
          {results.map((p) => (
            <li key={p.id}>
              <button onClick={() => choose(p)}>
                <span>
                  <strong>{p.name}</strong> · {p.brand} · {p.size}
                </span>
                <span className="muted">
                  {p.from_price === null ? "out of stock" : `from ${rupees(p.from_price)}`}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
