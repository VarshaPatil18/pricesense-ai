export const rupees = (n) => `₹${n}`;

export function feeTotal(fees) {
  return fees.delivery + fees.handling + fees.small_cart;
}

export function feeBreakdown(fees) {
  const parts = [];
  parts.push(fees.delivery ? `delivery ₹${fees.delivery}` : "free delivery");
  if (fees.handling) parts.push(`handling ₹${fees.handling}`);
  if (fees.small_cart) parts.push(`small cart ₹${fees.small_cart}`);
  return parts.join(" · ");
}
