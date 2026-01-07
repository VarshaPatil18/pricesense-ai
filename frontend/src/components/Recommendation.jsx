import { mockPrices } from "../data/mockPrices";

export default function Recommendation() {
  const best = mockPrices.reduce((a, b) =>
    a.total < b.total ? a : b
  );

  return (
    <div className="recommendation">
      <h2>🤖 AI Recommendation</h2>
      <p>
        <strong>{best.platform}</strong> is the best option right now.
      </p>
      <p>
        Lowest total price (₹{best.total}) with delivery in {best.time}.
      </p>
    </div>
  );
}


