import { useEffect, useRef } from "react";
import { Network } from "vis-network";

export default function VisGraph({ data }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!data || !data.nodes) return;

    const options = {
      layout: { improvedLayout: true },
      physics: {
        stabilization: false,
        barnesHut: { gravitationalConstant: -30000 }
      },
      groups: {
        ODP: { color: "#1976d2" },
        FDP: { color: "#2e7d32" },
        CDP: { color: "#ed6c02" },
        Table: { shape: "box" },
        Column: { shape: "ellipse" }
      },
      edges: {
        arrows: { to: { enabled: true } },
        font: { align: "middle" }
      }
    };

    networkRef.current = new Network(
      containerRef.current,
      data,
      options
    );

    return () => networkRef.current?.destroy();
  }, [data]);

  return (
    <div
      ref={containerRef}
      style={{ height: "100%", width: "100%" }}
    />
  );
}
