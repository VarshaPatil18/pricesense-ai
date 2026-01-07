export default function SearchBar({ onSearch }) {
  return (
    <div className="search-bar">
      <input placeholder="Search Milk, Rice, Sugar..." />
      <button onClick={onSearch}>Find Best Price</button>
    </div>
  );
}


