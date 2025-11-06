import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleStream = async () => {
    setResponse("");
    setLoading(true);

    const res = await fetch("http://127.0.0.1:8001/stream-query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = ""; // 🧠 accumulate small tokens here

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk
        .split("\n")
        .filter((line) => line.startsWith("data: "));

      for (const line of lines) {
        const data = line.replace("data: ", "").trim();
        if (data === "[DONE]") {
          setLoading(false);
          break;
        }

        // Append token to buffer
        buffer += data + " ";

        // ✅ Only update UI every few tokens (reduce flicker)
        if (buffer.length > 30) {
          console.log("🔹 Streamed chunk:", buffer.trim());
          setResponse((prev) => prev + buffer);
          buffer = "";
        }
      }
    }

    // Flush remaining buffer
    if (buffer) setResponse((prev) => prev + buffer);

    console.log("✅ Streaming completed");
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>🧠 MCP Agent Stream Demo</h1>
      <textarea
        rows="3"
        placeholder="Ask me anything..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <br />
      <button onClick={handleStream} disabled={loading}>
        {loading ? "Streaming..." : "Send Query"}
      </button>

      <div className="response-box">
        <h3>Response:</h3>
        {/* ✅ Render proper Markdown */}
        <ReactMarkdown>{response}</ReactMarkdown>
      </div>
    </div>
  );
}

export default App;
