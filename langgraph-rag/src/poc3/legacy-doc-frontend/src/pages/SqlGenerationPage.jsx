import React, { useMemo, useState } from "react";
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Divider,
  IconButton,
  Paper,
  Stack,
  TextField,
  ThemeProvider,
  Typography,
  createTheme
} from "@mui/material";
import {
  Brightness4,
  Brightness7,
  UploadFile,
  Send,
  AutoAwesome
} from "@mui/icons-material";
import { Link } from "react-router-dom";

import LineageGraph from "../components/LineageGraph";
import { uploadZip } from "../services/api";

export default function SqlGenerationPage() {
  const [mode, setMode] = useState("dark");
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Ask me for SQL and I will generate queries based on your data model."
    }
  ]);
  const [input, setInput] = useState("");

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: mode === "dark" ? "#1ed760" : "#0b5fff" },
          secondary: { main: mode === "dark" ? "#0b5fff" : "#1ed760" },
          background: {
            default: mode === "dark" ? "#0b0f0e" : "#f6f9ff",
            paper: mode === "dark" ? "#111716" : "#ffffff"
          },
          text: {
            primary: mode === "dark" ? "#f4f7f6" : "#0f1a2b",
            secondary: mode === "dark" ? "#b8c2bd" : "#51607a"
          }
        },
        shape: { borderRadius: 14 },
        typography: {
          fontFamily:
            '"Poppins","Montserrat","Segoe UI","Helvetica Neue",Arial,sans-serif'
        }
      }),
    [mode]
  );

  const handleUpload = async () => {
    if (!file) return;
    try {
      setUploadStatus("Uploading...");
      await uploadZip(file);
      setUploadStatus("Upload complete");
    } catch (err) {
      console.error("Upload failed", err);
      setUploadStatus("Upload failed");
    }
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    setMessages(prev => [
      ...prev,
      { role: "user", content: trimmed },
      {
        role: "assistant",
        content:
          "SQL generation placeholder. Connect this to your agent for real answers."
      }
    ]);
    setInput("");
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          background:
            mode === "dark"
              ? "radial-gradient(1100px 600px at 10% -10%, rgba(30,215,96,0.18), transparent 60%), radial-gradient(900px 500px at 90% 10%, rgba(11,95,255,0.14), transparent 55%), #0b0f0e"
              : "radial-gradient(900px 500px at 15% -10%, rgba(11,95,255,0.12), transparent 60%), radial-gradient(900px 500px at 85% 10%, rgba(30,215,96,0.12), transparent 55%), #f6f9ff"
        }}
      >
        <Container maxWidth="xl" sx={{ py: 5 }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 4
            }}
          >
            <Box>
              <Typography
                variant="h3"
                sx={{ fontWeight: 800, letterSpacing: 0.3 }}
              >
                SQL Generation Studio
              </Typography>
              <Typography sx={{ mt: 1, color: "text.secondary" }}>
                Upload docs, explore lineage, and chat for SQL.
              </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Button
                component={Link}
                to="/app"
                variant="outlined"
                color="secondary"
              >
                Back to Main
              </Button>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1.5,
                  px: 2,
                  py: 1,
                  borderRadius: 999,
                  bgcolor: "background.paper",
                  boxShadow: 3
                }}
              >
                <Typography sx={{ fontWeight: 600 }}>
                  {mode === "dark" ? "Dark" : "Light"} Mode
                </Typography>
                <IconButton
                  onClick={() =>
                    setMode(prev => (prev === "dark" ? "light" : "dark"))
                  }
                  color="primary"
                >
                  {mode === "dark" ? <Brightness7 /> : <Brightness4 />}
                </IconButton>
              </Box>
            </Box>
          </Box>

          <Stack spacing={3}>
            <Paper
              elevation={7}
              sx={{
                p: 3,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 2
              }}
            >
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Upload Documents
                </Typography>
                <Typography sx={{ color: "text.secondary", mt: 0.5 }}>
                  Add metadata or specs for better SQL generation.
                </Typography>
              </Box>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Button
                  component="label"
                  variant="outlined"
                  startIcon={<UploadFile />}
                >
                  Choose File
                  <input
                    type="file"
                    hidden
                    onChange={e => setFile(e.target.files?.[0] || null)}
                  />
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AutoAwesome />}
                  onClick={handleUpload}
                  disabled={!file}
                >
                  Upload
                </Button>
                <Typography sx={{ color: "text.secondary" }}>
                  {uploadStatus || (file ? file.name : "No file selected")}
                </Typography>
              </Box>
            </Paper>

            <Paper
              elevation={9}
              sx={{
                p: 2,
                height: "55vh",
                maxHeight: "55vh",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 1
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Vis.js Lineage Graph
                </Typography>
                <Box
                  sx={{
                    px: 1.5,
                    py: 0.5,
                    borderRadius: 999,
                    bgcolor:
                      mode === "dark"
                        ? "rgba(30,215,96,0.15)"
                        : "rgba(11,95,255,0.12)",
                    color: "primary.main",
                    fontWeight: 600,
                    fontSize: 12
                  }}
                >
                  Live View
                </Box>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ flex: 1, minHeight: 0, height: "100%" }}>
                <LineageGraph refresh={false} />
              </Box>
            </Paper>

            <Paper
              elevation={8}
              sx={{
                p: 3,
                height: "55vh",
                maxHeight: "55vh",
                display: "flex",
                flexDirection: "column"
              }}
            >
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 1
                }}
              >
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Chat for SQL
                </Typography>
                <Box
                  sx={{
                    px: 1.5,
                    py: 0.5,
                    borderRadius: 999,
                    bgcolor:
                      mode === "dark"
                        ? "rgba(30,215,96,0.12)"
                        : "rgba(11,95,255,0.12)",
                    color: "primary.main",
                    fontWeight: 600,
                    fontSize: 12
                  }}
                >
                  Ready
                </Box>
              </Box>
              <Divider sx={{ mb: 2 }} />

              <Box
                sx={{
                  flex: 1,
                  overflowY: "auto",
                  pr: 1,
                  mb: 2
                }}
              >
                {messages.map((msg, idx) => (
                  <Box
                    key={`${msg.role}-${idx}`}
                    sx={{
                      display: "flex",
                      justifyContent:
                        msg.role === "user" ? "flex-end" : "flex-start",
                      mb: 1.5
                    }}
                  >
                    <Box
                      sx={{
                        maxWidth: "70%",
                        px: 2,
                        py: 1.5,
                        borderRadius: 2,
                        bgcolor:
                          msg.role === "user"
                            ? "primary.main"
                            : mode === "dark"
                              ? "rgba(255,255,255,0.08)"
                              : "rgba(0,0,0,0.06)",
                        color:
                          msg.role === "user" ? "#ffffff" : "text.primary",
                        boxShadow: msg.role === "user" ? 4 : 0
                      }}
                    >
                      <Typography>{msg.content}</Typography>
                    </Box>
                  </Box>
                ))}
              </Box>

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 1.5,
                  borderRadius: 999,
                  border: "1px solid",
                  borderColor:
                    mode === "dark"
                      ? "rgba(255,255,255,0.12)"
                      : "rgba(0,0,0,0.1)",
                  px: 2,
                  py: 1
                }}
              >
                <TextField
                  fullWidth
                  variant="standard"
                  placeholder="Ask for SQL..."
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  InputProps={{ disableUnderline: true }}
                />
                <IconButton color="primary" onClick={handleSend}>
                  <Send />
                </IconButton>
              </Box>
            </Paper>
          </Stack>
        </Container>
      </Box>
    </ThemeProvider>
  );
}
