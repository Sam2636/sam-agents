import React, { useState } from "react";
import { Container, Typography, Box, Paper, Stack, Divider, Button, TextField } from "@mui/material";
import UploadForm from "../components/UploadForm";
import RepoPathForm from "../components/RepoPathForm";
import MetricsDashboard from "../components/MetricsDashboard";
import MarkdownPreview from "../components/MarkdownPreview";

export default function MainPage() {
  const [sessionId, setSessionId] = useState(null);

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      {/* Title */}
      <Typography
        variant="h3"
        align="center"
        sx={{
          mb: 5,
          fontWeight: "bold",
          color: "primary.main",
          textShadow: "0 3px 10px rgba(0,0,0,0.3)",
        }}
      >
        Transform Legacy Code into <span style={{ color: "#F4B400" }}>Smart Documentation</span>
      </Typography>

      <Box display="flex" gap={4}>
        {/* LEFT PANEL */}
        <Stack spacing={3} sx={{ width: "40%" }}>
          
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
              Upload Zip
            </Typography>
            <UploadForm onStart={setSessionId} />
          </Paper>

          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
              Use Local Repository Path
            </Typography>
            <RepoPathForm />
          </Paper>

          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
              Metrics Snapshot
            </Typography>
            <MetricsDashboard />
          </Paper>
        </Stack>

        {/* RIGHT PANEL — MARKDOWN PREVIEW */}
        <Paper elevation={4} sx={{ p: 3, width: "60%", minHeight: "70vh" }}>
          <MarkdownPreview sessionId={sessionId} />
        </Paper>
      </Box>
    </Container>
  );
}
