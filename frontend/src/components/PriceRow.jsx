export default function PriceRow({ item, isBest }) {
  return (
    
    <tr className={isBest ? "best" : ""}>
      <td>{item.platform}</td>
      <td>₹{item.price}</td>
      <td>{item.quantity}</td>
      <td>₹{item.delivery}</td>
      <td>₹{item.fee}</td>
      <td><strong>₹{item.total}</strong></td>
      <td>{item.time}</td>
      <td>
        <button className="order-btn">Order</button>
      </td>
    </tr>
    
  );
}



