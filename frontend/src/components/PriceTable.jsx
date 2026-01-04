export default function PriceTable({ prices }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Platform</th>
          <th>Price (₹)</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(prices).map(([platform, price]) => (
          <tr key={platform}>
            <td>{platform}</td>
            <td>₹{price}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
