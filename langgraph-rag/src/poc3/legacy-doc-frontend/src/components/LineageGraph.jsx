import { useEffect, useState } from "react";
import VisGraph from "./VisGraph";
import { fetchVisualGraph } from "../services/api";

export default function LineageGraph({ refresh, focusNodeId, onGraphLoaded, onNodeSelect }) {
  const [graph, setGraph] = useState(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let isActive = true;
    setHasError(false);

    fetchVisualGraph()
      .then((data) => {
        if (!isActive) return;
        console.log("VisJS graph API response:", data);
        setGraph(data);
        onGraphLoaded?.(data);
      })
      .catch((err) => {
        if (!isActive) return;
        console.error("VisJS graph API error:", err);
        setHasError(true);
      });

    return () => {
      isActive = false;
    };
  }, [refresh]);

  if (!graph) {
    return (
      <div style={{ color: "inherit", opacity: 0.75, padding: "8px 2px" }}>
        {hasError ? "Graph fetch failed." : "Loading graph..."}
      </div>
    );
  }

  return <VisGraph data={graph} focusNodeId={focusNodeId} onNodeSelect={onNodeSelect} />;
}
