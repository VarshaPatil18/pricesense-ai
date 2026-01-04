export default function SearchBar({ onSearch }) {
  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      onSearch(e.target.value);
    }
  };

  return (
    <input
      className="search"
      placeholder="Search product (e.g. milk, shampoo)"
      onKeyDown={handleKeyPress}
    />
  );
}
