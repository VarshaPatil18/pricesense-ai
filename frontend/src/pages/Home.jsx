import SearchBar from "../components/SearchBar";

export default function Home({ onSearch }) {
  return (
    <div className="container">
      <h1>PriceSense AI</h1>
      <p>
        AI-powered smart purchasing assistant that helps you find the best price
        and explains why.
      </p>
      <SearchBar onSearch={onSearch} />
    </div>
  );
}
