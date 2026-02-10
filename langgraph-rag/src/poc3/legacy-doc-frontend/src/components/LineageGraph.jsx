import { useEffect, useState } from "react";
import VisGraph from "./VisGraph";
import { fetchVisualGraph } from "../services/api";

export default function LineageGraph({ refresh }) {
  const [graph, setGraph] = useState(null);

  useEffect(() => {
    fetchVisualGraph()
      .then(data => {
        console.log("VisJS graph API response:", data);
        setGraph(data);
      })
      .catch(err => {
        console.error("VisJS graph API error:", err);
      });
  }, [refresh]);

  if (!graph) return "Loading graph...";

  return <VisGraph data={graph} />;
}
