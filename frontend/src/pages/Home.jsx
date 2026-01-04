import Header from "../components/Header";
import SearchBar from "../components/SearchBar";

export default function Home({ onSearch }) {
  return (
    <>
      <Header />
      <SearchBar onSearch={onSearch} />
    </>
  );
}
