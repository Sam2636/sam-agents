import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Paper
} from "@mui/material";
import axios from "axios";

const API_OPTIONS = [
  {
    label: "Table Metadata",
    value: "http://localhost:8000/metadata/table"
  },
  {
    label: "Table Lineage",
    value: "http://localhost:8000/metadata/lineage/table"
  },
  {
    label: "Column Lineage",
    value: "http://localhost:8000/metadata/lineage/column"
  },
  {
    label: "FK Lineage",
    value: "http://localhost:8000/metadata/lineage/fk"
  }
];

export default function MetadataIngestDialog({ open, onClose, onSuccess }) {
  const [selectedApi, setSelectedApi] = useState("");
  const [jsonData, setJsonData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target.result);
        setJsonData(parsed);
      } catch (err) {
        alert("Invalid JSON file");
      }
    };
    reader.readAsText(file);
  };

  const handleSubmit = async () => {
    if (!selectedApi || !jsonData) {
      alert("Select API and upload JSON");
      return;
    }

    try {
      setLoading(true);
      await axios.post(selectedApi, jsonData);
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      alert("Ingestion failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Upload Metadata</DialogTitle>

      <DialogContent dividers>
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          
          {/* API Selection */}
          <FormControl fullWidth>
            <InputLabel>Select Metadata Type</InputLabel>
            <Select
              value={selectedApi}
              label="Select Metadata Type"
              onChange={(e) => setSelectedApi(e.target.value)}
            >
              {API_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* File Upload */}
          <Button variant="outlined" component="label">
            Upload JSON File
            <input
              type="file"
              hidden
              accept=".json"
              onChange={handleFileUpload}
            />
          </Button>

          {/* JSON Preview */}
          {jsonData && (
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                maxHeight: 300,
                overflow: "auto",
                bgcolor: "background.default"
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                JSON Preview
              </Typography>
              <pre style={{ margin: 0, fontSize: 12 }}>
                {JSON.stringify(jsonData, null, 2)}
              </pre>
            </Paper>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Uploading..." : "Ingest Metadata"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
