import Header from "../components/Header";
import SearchBar from "../components/SearchBar";

export default function Home({ onSearch }) {
  return (
    <div className="container">
      <Header />

      <div className="home-card">
        <h2>Find the best deal instantly</h2>
        <p>
          Compare prices across Blinkit, Zepto, Swiggy Instamart and more.
          Our AI explains where and when to buy.
        </p>

        <SearchBar onSearch={onSearch} />
      </div>

      <div className="platforms">
  <div className="platform-card blinkit">Blinkit</div>
  <div className="platform-card zepto">Zepto</div>
  <div className="platform-card swiggy">Swiggy Instamart</div>
</div>

    </div>
  );
}


