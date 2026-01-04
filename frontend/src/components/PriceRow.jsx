export default function PriceRow({ item, isBest }) {
  return (
    <tr className={isBest ? "best" : ""}>
      <td>{item.platform}</td>
      <td>₹{item.price}</td>
      <td>₹{item.delivery}</td>
      <td>₹{item.fee}</td>
      <td><b>₹{item.total}</b></td>
      <td>
        <button className="order-btn">
          Order
        </button>
      </td>
    </tr>
  );
}
