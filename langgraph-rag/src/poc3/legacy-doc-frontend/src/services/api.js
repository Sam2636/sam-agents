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
