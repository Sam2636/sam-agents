import React, { useMemo, useState, useRef, useEffect } from "react";
import {
  Box, Button, Container, CssBaseline, Divider, IconButton, Paper,
  Stack, TextField, ThemeProvider, Typography, createTheme, CircularProgress, Fade
} from "@mui/material";
import {
  Brightness4, Brightness7, UploadFile, Send, AutoAwesome,
  ContentCopy, Check, Storage
} from "@mui/icons-material";
import { Link } from "react-router-dom";
import LineageGraph from "../components/LineageGraph";

// --- SQL DISPLAY COMPONENT ---
const SqlDisplay = ({ sql }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Box sx={{ mt: 1.5, borderRadius: 2, overflow: "hidden", border: "1px solid rgba(255,255,255,0.1)", width: "100%", boxShadow: 4 }}>
      <Box sx={{ bgcolor: "#2d2d2d", px: 2, py: 0.8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="caption" sx={{ color: "#1ed760", fontWeight: 700, letterSpacing: 1 }}>PROPOSED SQL</Typography>
        <Button size="small" startIcon={copied ? <Check /> : <ContentCopy />} onClick={handleCopy} sx={{ color: copied ? "#1ed760" : "#aaa", fontSize: 10 }}>
          {copied ? "COPIED" : "COPY"}
        </Button>
      </Box>
      <Box sx={{ p: 2, bgcolor: "#111", color: "#d4d4d4", fontFamily: "'Fira Code', monospace", fontSize: "0.85rem", whiteSpace: "pre-wrap" }}>
        {sql}
      </Box>
    </Box>
  );
};

export default function SqlGenerationPage() {
  const [mode, setMode] = useState("dark");
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState("");
  
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("sql_session_id") || "";
  });

  const [messages, setMessages] = useState([
    { role: "assistant", content: "Ready. Upload a CSV or ask a question about the existing model." }
  ]);

  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const theme = useMemo(() => createTheme({
    palette: {
      mode,
      primary: { main: mode === "dark" ? "#1ed760" : "#0b5fff" },
      background: {
        default: mode === "dark" ? "#0b0f0e" : "#f6f9ff",
        paper: mode === "dark" ? "#111716" : "#ffffff"
      },
    },
    shape: { borderRadius: 14 },
    typography: { fontFamily: '"Poppins","Montserrat",sans-serif' }
  }), [mode]);

  // --- UPLOAD HANDLER (PORT 8080) ---
  const handleUpload = async () => {
    if (!file) return;
    try {
      setUploadStatus("Uploading...");
      const formData = new FormData();
      // Using "files" based on your previous logs
      formData.append("files", file); 

      const response = await fetch("http://localhost:8080/csv/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");
      
      const data = await response.json();
      
      if (data.session_id) {
        localStorage.setItem("sql_session_id", data.session_id);
        setSessionId(data.session_id);
      }

      setUploadStatus("Success!");
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: `Upload complete! Session ${data.session_id?.substring(0,8)} is active.` 
      }]);
    } catch (err) {
      console.error("Upload Error:", err);
      setUploadStatus("Failed");
    }
  };

  // --- SEND HANDLER (PORT 8080) ---
  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    if (!sessionId) {
      setMessages(prev => [...prev, { role: "assistant", content: "No active session. Please upload a file first." }]);
      return;
    }

    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Use normal chat endpoint for conversational turns.
      const endpoint = `http://localhost:8080/chat/`;
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: input })
      });
      
      if (!response.ok) {
        const errorDetail = await response.text();
        console.error("Agent Response Error:", errorDetail);
        throw new Error("Agent communication failed");
      }

      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: data.chat_reply || data.response || "I processed that request.", 
        sql: data.sql 
      }]);
    } catch (err) {
      console.error("Fetch Error:", err);
      setMessages(prev => [...prev, { role: "assistant", content: "System error: Failed to communicate with Agent. Check CORS or Session ID." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        height: "100vh", width: "100vw", overflow: "hidden", display: "flex", flexDirection: "column",
        background: mode === "dark" 
          ? "radial-gradient(1100px 600px at 10% -10%, rgba(30,215,96,0.15), transparent 60%), #0b0f0e" 
          : "radial-gradient(900px 500px at 15% -10%, rgba(11,95,255,0.1), transparent 60%), #f6f9ff"
      }}>
        <Container maxWidth="xl" sx={{ height: "100%", display: "flex", flexDirection: "column", py: 3 }}>
          
          {/* TOP HEADER */}
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 3, flexShrink: 0 }}>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, letterSpacing: -1 }}>SQL Generation Studio</Typography>
              <Typography sx={{ color: "text.secondary" }}>Port 8080 Active</Typography>
            </Box>
            <Stack direction="row" spacing={2} alignItems="center">
              <Button component={Link} to="/app" variant="outlined" color="inherit" sx={{ borderRadius: 10 }}>Back to Main</Button>
              <IconButton onClick={() => setMode(m => m === "dark" ? "light" : "dark")} color="primary">
                {mode === "dark" ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Stack>
          </Box>

          {/* UPLOAD STRIP */}
          <Paper elevation={8} sx={{ p: 2, mb: 3, display: "flex", alignItems: "center", justifyContent: "space-between", borderRadius: 4, flexShrink: 0 }}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Button component="label" variant="outlined" startIcon={<UploadFile />} sx={{ borderRadius: 10 }}>
                Choose File <input type="file" hidden onChange={e => { setFile(e.target.files?.[0]); setUploadStatus(""); }} />
              </Button>
              <Button 
                variant="contained" 
                startIcon={uploadStatus === "Uploading..." ? <CircularProgress size={20} color="inherit" /> : <AutoAwesome />} 
                onClick={handleUpload} 
                disabled={!file || uploadStatus === "Uploading..."}
                color={uploadStatus === "Success!" ? "success" : "primary"}
              >
                {uploadStatus === "Success!" ? "Uploaded" : "Upload to Server"}
              </Button>
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                {file ? file.name : (sessionId ? "Session Active" : "No file selected")}
              </Typography>
            </Stack>
            <Box sx={{ px: 2, py: 0.5, bgcolor: "rgba(30,215,96,0.1)", borderRadius: 5, color: "primary.main", fontWeight: 700, fontSize: 12 }}>
              SESSION: {sessionId ? sessionId.substring(0, 8) : "NONE"}
            </Box>
          </Paper>

          {/* MAIN WORKSPACE */}
          <Box sx={{ flex: 1, display: "grid", gridTemplateColumns: { md: "1.2fr 1fr" }, gap: 3, minHeight: 0, mb: 2 }}>
            <Paper elevation={12} sx={{ display: "flex", flexDirection: "column", overflow: "hidden", bgcolor: "#000", position: "relative" }}>
              <Box sx={{ p: 2, display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
                <Typography variant="h6" sx={{ fontWeight: 700, fontSize: 16 }}>Vis.js Lineage Graph</Typography>
                <Typography variant="caption" sx={{ color: "primary.main", fontWeight: 800 }}>LIVE VIEW</Typography>
              </Box>
              <Box sx={{ flex: 1, position: "relative" }}>
                <LineageGraph />
              </Box>
            </Paper>

            <Paper elevation={12} sx={{ display: "flex", flexDirection: "column", overflow: "hidden", border: "1px solid rgba(255,255,255,0.05)" }}>
              <Box sx={{ p: 2, borderBottom: "1px solid rgba(255,255,255,0.05)", display: "flex", justifyContent: "space-between" }}>
                <Typography variant="h6" sx={{ fontWeight: 700, fontSize: 16 }}>Chat for SQL</Typography>
                <Storage sx={{ color: "primary.main", fontSize: 18 }} />
              </Box>

              <Box ref={scrollRef} sx={{ flex: 1, overflowY: "auto", p: 3, display: "flex", flexDirection: "column", gap: 3 }}>
                {messages.map((msg, idx) => (
                  <Fade in={true} key={idx}>
                    <Box sx={{ alignSelf: msg.role === "user" ? "flex-end" : "flex-start", maxWidth: "90%" }}>
                      <Box sx={{ 
                        p: 2, borderRadius: 3, 
                        bgcolor: msg.role === "user" ? "primary.main" : "background.default",
                        color: msg.role === "user" ? "#fff" : "text.primary",
                        boxShadow: 3,
                        border: msg.role === "assistant" ? "1px solid rgba(255,255,255,0.05)" : "none"
                      }}>
                        <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{msg.content}</Typography>
                      </Box>
                      {msg.sql && <SqlDisplay sql={msg.sql} />}
                    </Box>
                  </Fade>
                ))}
                {loading && <CircularProgress size={24} sx={{ m: 2, alignSelf: "center" }} />}
              </Box>

              <Box sx={{ p: 2, bgcolor: "background.paper" }}>
                <Box sx={{ display: "flex", gap: 1, alignItems: "center", bgcolor: "background.default", p: 1, borderRadius: 10, border: "1px solid rgba(255,255,255,0.1)" }}>
                  <TextField 
                    fullWidth variant="standard" placeholder="Ask for SQL..." 
                    value={input} onChange={e => setInput(e.target.value)}
                    onKeyPress={e => e.key === 'Enter' && handleSend()}
                    InputProps={{ disableUnderline: true, sx: { px: 2 } }}
                  />
                  <IconButton color="primary" onClick={handleSend} disabled={loading} sx={{ bgcolor: "primary.main", color: "#000", "&:hover": { bgcolor: "primary.dark" } }}>
                    <Send fontSize="small" />
                  </IconButton>
                </Box>
              </Box>
            </Paper>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}
