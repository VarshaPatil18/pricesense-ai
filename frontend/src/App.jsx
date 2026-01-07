import { useState } from "react";
import Home from "./pages/Home";
import Compare from "./pages/Compare";
import "./styles.css";

export default function App() {
  const [showCompare, setShowCompare] = useState(false);

  return showCompare ? (
    <Compare />
  ) : (
    <Home onSearch={() => setShowCompare(true)} />
  );
}


