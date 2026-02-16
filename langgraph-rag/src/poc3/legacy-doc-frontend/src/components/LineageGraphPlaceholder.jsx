import { useEffect, useRef } from "react";
import { fetchCanvasLineageGraph } from "../services/api";

export default function LineageGraphPlaceholder({ refresh }) {
  const canvasRef = useRef(null);
  const graphRef = useRef(null);

  useEffect(() => {
    let isActive = true;

    fetchCanvasLineageGraph()
      .then((data) => {
        if (!isActive) return;
        graphRef.current = data;
        window.dispatchEvent(new Event("canvas-lineage-data-updated"));
      })
      .catch((err) => {
        if (!isActive) return;
        console.error("Canvas lineage API error:", err);
        graphRef.current = null;
        window.dispatchEvent(new Event("canvas-lineage-data-updated"));
      });

    return () => {
      isActive = false;
    };
  }, [refresh]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const draw = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();

      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));

      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      const w = rect.width;
      const h = rect.height;

      ctx.clearRect(0, 0, w, h);
      const graphData = graphRef.current;

      // Grid
      ctx.strokeStyle = "rgba(255,255,255,0.03)";
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      const layers = graphData?.layers?.length ? graphData.layers : ["ODP", "FDP", "CDP"];
      const sourceNodes = graphData?.nodes?.length
        ? graphData.nodes
        : layers.flatMap((layer, li) =>
            Array.from({ length: 3 + ((li + 1) % 2) }).map((_, i) => ({
              id: `${layer}_T${i + 1}`,
              label: `${layer}_T${i + 1}`,
              layer
            }))
          );

      const grouped = layers.reduce((acc, layer) => {
        acc[layer] = sourceNodes.filter((n) => n.layer === layer);
        return acc;
      }, {});

      const nodes = [];
      layers.forEach((layer, li) => {
        const layerNodes = grouped[layer] || [];
        const cx = (w / (layers.length + 1)) * (li + 1);
        layerNodes.forEach((node, i) => {
          const x = typeof node.x === "number" ? (node.x <= 1 ? node.x * w : node.x) : cx;
          const y =
            typeof node.y === "number"
              ? node.y <= 1
                ? node.y * h
                : node.y
              : (h / (layerNodes.length + 1)) * (i + 1);
          nodes.push({
            id: node.id || `${layer}_${i + 1}`,
            x,
            y,
            label: node.label || node.id || `${layer}_${i + 1}`,
            layerIndex: li
          });
        });
      });
      const nodeMap = new Map(nodes.map((n) => [n.id, n]));
      const edges = graphData?.edges?.length
        ? graphData.edges
        : nodes
            .flatMap((from) =>
              nodes
                .filter((to) => to.layerIndex === from.layerIndex + 1)
                .filter((_, i) => i % 2 === 0)
                .map((to) => ({ from: from.id, to: to.id }))
            );

      // Edges
      ctx.lineWidth = 1.5;
      edges.forEach((edge) => {
        const node = nodeMap.get(edge.from);
        const target = nodeMap.get(edge.to);
        if (!node || !target) return;
        const gradient = ctx.createLinearGradient(node.x, node.y, target.x, target.y);
        gradient.addColorStop(0, "rgba(30,215,96,0.3)");
        gradient.addColorStop(1, "rgba(11,95,255,0.3)");
        ctx.strokeStyle = gradient;
        ctx.beginPath();
        ctx.moveTo(node.x, node.y);
        const cpx = (node.x + target.x) / 2;
        ctx.bezierCurveTo(cpx, node.y, cpx, target.y, target.x, target.y);
        ctx.stroke();
      });

      const colors = ["rgba(30,215,96,0.9)", "rgba(11,95,255,0.9)", "rgba(120,80,255,0.9)"];
      const bgColors = ["rgba(30,215,96,0.12)", "rgba(11,95,255,0.12)", "rgba(120,80,255,0.12)"];

      // Nodes
      nodes.forEach((node) => {
        const roundRect = (x, y, width, height, radius) => {
          ctx.beginPath();
          if (typeof ctx.roundRect === "function") {
            ctx.roundRect(x, y, width, height, radius);
          } else {
            const r = Math.min(radius, width / 2, height / 2);
            ctx.moveTo(x + r, y);
            ctx.arcTo(x + width, y, x + width, y + height, r);
            ctx.arcTo(x + width, y + height, x, y + height, r);
            ctx.arcTo(x, y + height, x, y, r);
            ctx.arcTo(x, y, x + width, y, r);
            ctx.closePath();
          }
        };

        ctx.shadowColor = colors[node.layerIndex] || colors[0];
        ctx.shadowBlur = 15;
        ctx.fillStyle = bgColors[node.layerIndex] || bgColors[0];
        roundRect(node.x - 45, node.y - 16, 90, 32, 8);
        ctx.fill();

        ctx.shadowBlur = 0;
        ctx.strokeStyle = colors[node.layerIndex] || colors[0];
        ctx.lineWidth = 1;
        roundRect(node.x - 45, node.y - 16, 90, 32, 8);
        ctx.stroke();

        ctx.fillStyle = "rgba(255,255,255,0.9)";
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(node.label, node.x, node.y);
      });

      // Layer labels
      layers.forEach((layer, li) => {
        const cx = (w / 4) * (li + 1);
        ctx.fillStyle = "rgba(255,255,255,0.25)";
        ctx.font = "bold 13px 'Inter', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(`${layer} Layer`, cx, 30);
      });
    };

    draw();
    window.addEventListener("resize", draw);
    window.addEventListener("canvas-lineage-data-updated", draw);
    return () => {
      window.removeEventListener("resize", draw);
      window.removeEventListener("canvas-lineage-data-updated", draw);
    };
  }, [refresh]);

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full rounded-md"
      style={{ display: "block", width: "100%", height: "100%" }}
    />
  );
}
