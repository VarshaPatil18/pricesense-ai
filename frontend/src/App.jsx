import { useState } from "react";
import Home from "./pages/Home";
import Compare from "./pages/Compare";

export default function App() {
  const [product, setProduct] = useState(null);

  return (
    <>
      {!product ? (
        <Home onSearch={setProduct} />
      ) : (
        <Compare product={product} />
      )}
    </>
  );
}
