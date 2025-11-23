import { useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  CircularProgress,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { motion } from "framer-motion";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import Sidebar from "../components/Sidebar";
import ChatIcon from "@mui/icons-material/AutoAwesome";
import EditIcon from "@mui/icons-material/Edit";
import SearchIcon from "@mui/icons-material/Search";
import ImageIcon from "@mui/icons-material/Image";
import StarIcon from "@mui/icons-material/Star";
import { Avatar } from "@mui/material";


const MotionPaper = motion(Paper);

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef();

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [messages]);

  const fixSpacing = (prev, chunk) => {
    if (!prev) return chunk;
    if (!chunk.startsWith(" ") && !chunk.match(/^[.,!?;:]/)) {
      return prev + " " + chunk;
    }
    return prev + chunk;
  };
const handleFileUpload = (e) => {
  const file = e.target.files?.[0];
  if (file) {
    console.log("Uploaded:", file.name);
  }
};

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((p) => [...p, { role: "user", text: input }]);
    setMessages((p) => [...p, { role: "ai", text: "" }]);
    setLoading(true);

    const res = await fetch(
      `http://localhost:8000/joke/stream?topic=${input}`,
      { headers: { Accept: "text/event-stream" } }
    );

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    setInput("");

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk
        .split("\n")
        .filter((line) => line.startsWith("data: "));

      for (const line of lines) {
        const data = line.replace("data: ", "").trim();
        if (data === "[DONE]") {
          setLoading(false);
          return;
        }

        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1].text = fixSpacing(
            updated[updated.length - 1].text,
            data
          );
          return updated;
        });
      }
    }
    setLoading(false);
  };
return (
  <Box display="flex" height="100vh" bgcolor="#ffffff">

    {/* LEFT FIXED SIDEBAR */}
    <Box
      width="60px"
      display={{ xs: "none", md: "flex" }}
      flexDirection="column"
      alignItems="center"
      justifyContent="space-between"
      py={3}
      sx={{
        borderRight: "1px solid #eee",
        position: "fixed",
        left: 0,
        top: 0,
        bottom: 0,
        bgcolor: "#fff",
      }}
    >
      {/* Top Icons */}
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <IconButton sx={{ width: 32, height: 32 }}>
          <ChatIcon fontSize="small" />
        </IconButton>
        <IconButton sx={{ width: 32, height: 32 }}>
          <EditIcon fontSize="small" />
        </IconButton>
        <IconButton sx={{ width: 32, height: 32 }}>
          <SearchIcon fontSize="small" />
        </IconButton>
        <IconButton sx={{ width: 32, height: 32 }}>
          <ImageIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Bottom Icons */}
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <IconButton sx={{ width: 32, height: 32 }}>
          <StarIcon fontSize="small" />
        </IconButton>

        <Avatar
          src="/path/to/profile.jpg"
          sx={{ width: 32, height: 32 }}
        />
      </Box>
    </Box>

    {/* MAIN CONTENT WRAPPER (centers the chat column) */}
    <Box
      display="flex"
      justifyContent="center"
      flexGrow={1}
      ml={{ xs: 0, md: "60px" }}   // Only push enough to NOT hide behind sidebar
    >

      {/* CHAT COLUMN */}
      <Box
        display="flex"
        flexDirection="column"
        flexGrow={1}
        maxWidth="900px"
        width="100%"
        px={2}
      >

        {/* HEADER */}
        <Box
          p={2}
          textAlign="center"
          fontWeight="600"
          fontSize="18px"
          bgcolor="#fff"
        >
          💬 AI Chat Assistant
        </Box>

        {/* CHAT MESSAGES AREA */}
        <Box
  flex={1}
  overflow="auto"
  p={3}
  display="flex"
  flexDirection="column"
  gap={2}
  sx={{
    "&::-webkit-scrollbar": { display: "none" },   // Chrome, Edge
    "-ms-overflow-style": "none",                  // IE + Edge
    "scrollbar-width": "none",                     // Firefox
  }}
>

          {messages.map((msg, i) => (
            <MotionPaper
              key={i}
              elevation={0}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              sx={{
                alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                bgcolor: msg.role === "user" ? "#e8f0fe" : "#f7f7f8",
                color: "#111",
                p: 2,
                borderRadius: 3,
                maxWidth: "85%",
                boxShadow: "none",
                border: "none",
              }}
            >
              <Typography sx={{ whiteSpace: "pre-wrap" }}>
                {msg.text}
              </Typography>
            </MotionPaper>
          ))}
          <div ref={chatEndRef} />
        </Box>

        {/* INPUT BAR */}
        <Box
          p={2}
          bgcolor="#fff"
          display="flex"
          gap={1}
          alignItems="center"
        >
          <Paper
            elevation={0}
            sx={{
              display: "flex",
              alignItems: "center",
              flexGrow: 1,
              px: 2,
              py: 0.8,
              borderRadius: "30px",
              bgcolor: "#f7f7f8",
              gap: 1,
              border: "none",
              boxShadow: "none",
            }}
          >
            {/* Upload */}
            <IconButton component="label" sx={{ padding: 0.5 }}>
              <input hidden type="file" onChange={handleFileUpload} />
              <UploadFileIcon fontSize="small" />
            </IconButton>

            {/* Input */}
            <TextField
              fullWidth
              placeholder="Message Chat..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                sx: { fontSize: "16px" },
              }}
              sx={{ mx: 1 }}
            />

            {/* Send */}
            <IconButton
              onClick={sendMessage}
              sx={{
                bgcolor: "#0f8df2",
                color: "#fff",
                width: 40,
                height: 40,
                borderRadius: "50%",
                "&:hover": { bgcolor: "#0077d8" },
              }}
            >
              <SendIcon />
            </IconButton>
          </Paper>
        </Box>
      </Box>
    </Box>
  </Box>
);


}
