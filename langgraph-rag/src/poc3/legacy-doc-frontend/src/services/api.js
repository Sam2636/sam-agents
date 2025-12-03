import axios from "axios";

const API_BASE = "http://localhost:8000"; // FastAPI backend

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
