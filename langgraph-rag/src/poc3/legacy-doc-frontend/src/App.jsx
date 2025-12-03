import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import RepoPathForm from "./components/RepoPathForm";
import MetricsDashboard from "./components/MetricsDashboard";

function App() {
  const [sessionId, setSessionId] = useState(null);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Legacy Documentation Agent</h1>

      <h2>Option 1: Upload Zip</h2>
      <UploadForm onStart={setSessionId} />

      <h2>Option 2: Repo Path</h2>
      <RepoPathForm />

      <h2>Metrics Dashboard</h2>
      <MetricsDashboard />
    </div>
  );
}

export default App;
