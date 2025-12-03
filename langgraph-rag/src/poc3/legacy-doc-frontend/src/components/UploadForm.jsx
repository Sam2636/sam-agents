import React, { useState } from "react";
import { uploadZip, startProcessing } from "../services/api";

export default function UploadForm({ onStart }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Select a zip file");

    try {
      // 1️⃣ Upload zip
      const res = await uploadZip(file);
      const session_id = res.data.session_id;
      alert("Uploaded! Session ID: " + session_id);

      // 2️⃣ Start processing
      const startRes = await startProcessing({ session_id });
      alert("Processing started: " + startRes.data.status);

      // optional callback
      if (onStart) onStart(session_id);
    } catch (err) {
      console.error(err);
      alert("Error uploading or starting processing: " + err.message);
    }
  };

  return (
    <div>
      <input type="file" accept=".zip" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload & Start</button>
    </div>
  );
}
