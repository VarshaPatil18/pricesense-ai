export default function SearchBar({ onSearch }) {
  return (
    <div className="search-bar">
      <input placeholder="Search Milk, Atta, Rice..." />
      <button onClick={onSearch}>Compare Prices</button>
    </div>
  );
}
