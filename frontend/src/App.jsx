import { useState } from "react";
import Home from "./pages/Home";
import Compare from "./pages/Compare";

export default function App() {
  const [showCompare, setShowCompare] = useState(false);

  return (
    <div className="container">
      {showCompare
        ? <Compare />
        : <Home onSearch={() => setShowCompare(true)} />}
    </div>
  );
}
