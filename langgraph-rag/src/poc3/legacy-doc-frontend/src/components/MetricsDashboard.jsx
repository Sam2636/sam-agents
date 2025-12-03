import React, { useEffect, useState } from "react";
import { fetchMetrics } from "../services/api";

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState({ folders: 0, files: 0, tokens: 0 });

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetchMetrics();
      setMetrics(res.data);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h3>Progress</h3>
      <p>Folders Processed: {metrics.folders}</p>
      <p>Files Processed: {metrics.files}</p>
      <p>Tokens Used: {metrics.tokens}</p>
    </div>
  );
}
