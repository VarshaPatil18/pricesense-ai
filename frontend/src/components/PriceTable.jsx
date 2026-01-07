import PriceRow from "./PriceRow";
import { mockPrices } from "../data/mockPrices";

export default function PriceTable() {
  const cheapest = Math.min(...mockPrices.map(p => p.total));

  return (
    <table>
      <thead>
        <tr>
          <th>Platform</th>
          <th>Price</th>
          <th>Qty</th>
          <th>Delivery</th>
          <th>Fee</th>
          <th>Total</th>
          <th>ETA</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {mockPrices.map(item => (
          <PriceRow
            key={item.platform}
            item={item}
            isBest={item.total === cheapest}
          />
        ))}
      </tbody>
    </table>
  );
}


