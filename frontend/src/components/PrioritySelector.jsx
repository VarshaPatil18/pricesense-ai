const OPTIONS = [
  { id: "cheapest", label: "Lowest price" },
  { id: "balanced", label: "Balanced" },
  { id: "fastest", label: "Fastest" },
];

export default function PrioritySelector({ value, onChange }) {
  return (
    <div className="priority" role="radiogroup" aria-label="What matters most">
      <span className="muted">What matters most?</span>
      {OPTIONS.map((o) => (
        <button
          key={o.id}
          role="radio"
          aria-checked={value === o.id}
          className={value === o.id ? "chip active" : "chip"}
          onClick={() => onChange(o.id)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
