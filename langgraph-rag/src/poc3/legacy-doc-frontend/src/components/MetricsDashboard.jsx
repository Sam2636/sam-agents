import React, { useEffect, useState } from "react";
import { fetchMetrics } from "../services/api";

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState({ folders: 0, files: 0, tokens: 0 });

  useEffect(() => {
    let isMounted = true;
    let intervalId = null;

    const getMetrics = async () => {
      try {
        const res = await fetchMetrics();
        if (isMounted) {
          setMetrics({
            folders: res.data.folders_processed,
            files: res.data.files_processed,
            tokens: res.data.tokens_used,
          });
          // console.log("Fetched metrics:", res.data);
        }
      } catch (err) {
        // console.error("Metrics fetch failed:", err);
        // Optional: Set an error state or show a notification
      }
    };

    getMetrics();
    intervalId = setInterval(getMetrics, 5000); // Increased interval to 5s

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
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
