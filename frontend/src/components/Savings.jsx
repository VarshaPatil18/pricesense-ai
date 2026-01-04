export default function Savings({ prices }) {
  const values = Object.values(prices);
  if (values.length === 0) return null;

  const max = Math.max(...values);
  const min = Math.min(...values);

  return (
    <div className="savings">
      <h3>You Saved ₹{max - min}</h3>
      <p>Making smarter purchases with AI.</p>
    </div>
  );
}
