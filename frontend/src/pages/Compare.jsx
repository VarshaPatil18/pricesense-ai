import { useEffect, useState } from "react";
import PriceTable from "../components/PriceTable";
import Recommendation from "../components/Recommendation";
import Savings from "../components/Savings";

export default function Compare({ product }) {
  const [prices, setPrices] = useState({});
  const [recommendation, setRecommendation] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8000/products/${product}`)
      .then((res) => res.json())
      .then(setPrices);

    fetch(`http://localhost:8000/recommend/${product}`)
      .then((res) => res.json())
      .then(setRecommendation);
  }, [product]);

  return (
    <div className="container">
      <h2>Price Comparison for {product}</h2>

      <PriceTable prices={prices} />

      {recommendation && (
        <>
          <Recommendation data={recommendation} />
          <Savings prices={prices} />
        </>
      )}
    </div>
  );
}
