import React, { useState } from "react";
import { startProcessing } from "../services/api";

export default function RepoPathForm() {
  const [path, setPath] = useState("");

  const handleStart = async () => {
    if (!path) return alert("Enter repo path");
    await startProcessing({ path });
    alert("Processing started for " + path);
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Enter local repo path"
        value={path}
        onChange={(e) => setPath(e.target.value)}
      />
      <button onClick={handleStart}>Start Processing</button>
    </div>
  );
}
