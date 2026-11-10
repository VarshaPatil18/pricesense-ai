import { feeBreakdown, feeTotal, rupees } from "../utils/format";

export default function PriceTable({ offers, showUnitPrice = false }) {
  if (offers.length === 0) return null;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Platform</th>
            <th>Items</th>
            <th>Fees</th>
            <th>Total</th>
            <th>Delivery</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {offers.map((o, i) => (
            <tr key={o.platform_id} className={i === 0 ? "best" : ""}>
              <td>
                <strong>{o.platform}</strong>
                {i === 0 && <span className="badge">Best</span>}
              </td>
              <td>
                {rupees(o.subtotal)}
                {showUnitPrice && o.unit_price_label && (
                  <small>{o.unit_price_label}</small>
                )}
              </td>
              <td>
                {rupees(feeTotal(o.fees))}
                <small>{feeBreakdown(o.fees)}</small>
              </td>
              <td>
                <strong>{rupees(o.total)}</strong>
              </td>
              <td>{o.eta_minutes} min</td>
              <td>{o.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
