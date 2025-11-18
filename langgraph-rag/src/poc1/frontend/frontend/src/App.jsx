import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  // 🟢 Fix spacing between streamed chunks
  const fixSpacing = (prev, chunk) => {
    if (!prev) return chunk; // first chunk, no fix needed

    // If chunk does not start with space/punctuation → add a space
    if (!chunk.startsWith(" ") && !chunk.match(/^[.,!?;:]/)) {
      return prev + " " + chunk;
    }

    return prev + chunk;
  };

  const handleStream = async () => {
    setResponse("");
    setLoading(true);

    const res = await fetch(`http://localhost:8000/joke/stream?topic=${query}`, {
      method: "GET",
      headers: { Accept: "text/event-stream" },
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

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

        console.log("🔹 Streamed:", data);

        // 🟢 Apply spacing fix here
        setResponse((prev) => fixSpacing(prev, data));
      }
    }

    setLoading(false);
  };

  return (
    <div className="App">
      <h1>😺 Joke Generator (Streaming)</h1>

      <textarea
        rows="3"
        placeholder="Enter a topic... e.g., Cats"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <br />
      <button onClick={handleStream} disabled={loading}>
        {loading ? "Streaming..." : "Generate Joke"}
      </button>

      <div className="response-box">
        <h3>Response:</h3>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default App;
