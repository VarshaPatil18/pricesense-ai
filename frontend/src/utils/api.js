const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new Error("Cannot reach the PriceSense API. Is the backend running?");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body && typeof body.detail === "string" ? body.detail : null;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return body;
}

export function searchProducts(q, limit = 8) {
  return request(`/products?${new URLSearchParams({ q, limit })}`);
}

export function getHealth() {
  return request("/health");
}

export function compareProduct({ productId, qty, priority, explain }) {
  const params = new URLSearchParams({ product_id: productId, qty, priority, explain });
  return request(`/compare?${params}`);
}

export function compareBasket({ items, priority, explain }) {
  return request("/basket", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items, priority, explain }),
  });
}
