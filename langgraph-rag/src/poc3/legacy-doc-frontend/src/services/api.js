import axios from "axios";

const API_BASE = ""; // Use relative path for Vite proxy

export const uploadZip = (file) => {
  const form = new FormData();
  form.append("file", file);
  return axios.post(`${API_BASE}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const startProcessing = (data) => {
  // data: { path: "..."} or { session_id: "..." }
  return axios.post(`${API_BASE}/start`, data);
};

export const stopProcessing = () => {
  return axios.post(`${API_BASE}/stop`);
};

export const fetchMetrics = () => {
  return axios.get(`${API_BASE}/metrics`);
};

export const fetchMarkdown = (sessionId) => {
  return axios.get(`${API_BASE}/markdown/${sessionId}`);
};

export const fetchGraphMetrics = () =>
  axios.get("http://localhost:8000/metadata/graph/metrics");

export const fetchVisualGraph = () =>
  fetch("http://localhost:8000/metadata/graph/visual")
    .then(res => res.json());

export const fetchCanvasLineageGraph = () =>
  fetch("http://localhost:8000/metadata/graph/canvas")
    .then((res) => {
      if (!res.ok) throw new Error(`Canvas API error: ${res.status}`);
      return res.json();
    });

export const fetchTableCanvasLineage = () =>
  fetch("http://localhost:8000/metadata/canvas")
    .then((res) => {
      if (!res.ok) throw new Error(`Table canvas API error: ${res.status}`);
      return res.json();
    });

export const fetchColumnCanvasLineage = () =>
  fetch("http://localhost:8000/metadata/columns")
    .then((res) => {
      if (!res.ok) throw new Error(`Column canvas API error: ${res.status}`);
      return res.json();
    });

export const dropAllMetadataGraph = () =>
  fetch("http://localhost:8000/metadata/admin/drop-all", { method: "DELETE" })
    .then((res) => {
      if (!res.ok) throw new Error(`Drop graph API error: ${res.status}`);
      return res.json();
    });
