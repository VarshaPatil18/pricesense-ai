import SearchBar from "../components/SearchBar";
import Recommendation from "../components/Recommendation";
import PriceTable from "../components/PriceTable";

export default function Compare() {
  return (
    <div className="container">
      <SearchBar />
      <Recommendation />
      <PriceTable />
    </div>
  );
}

