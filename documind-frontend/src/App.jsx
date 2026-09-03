import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [stats, setStats] = useState(null);


  const fetchStats = async () => {
  const res = await fetch("https://documind-production-dc80.up.railway.app/stats");
  const data = await res.json();
  setStats(data);
};


  const handleUpload = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  setUploadStatus("Uploading...");

  const res = await fetch("https://documind-production-dc80.up.railway.app/upload", {
    method: "POST",
    body: formData,
  });
  const data = await res.json();

  setUploadStatus(`Uploaded — ${data.chunks_stored} chunks stored`);
};

const handleAsk = async () => {
  if (!question.trim()) return;

  const userMsg = { role: "user", text: question };
  setMessages((prev) => [...prev, userMsg]);
  setQuestion("");
  setLoading(true);

  const res = await fetch("https://documind-production-dc80.up.railway.app/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: userMsg.text }),
  });

  setLoading(false);

  const botMsg = { role: "bot", text: "", sources: [] };
  setMessages((prev) => [...prev, botMsg]);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let sourcesParsed = false;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    if (!sourcesParsed) {
      const delimiterIndex = buffer.indexOf("<<<END_SOURCES>>>\n");
      if (delimiterIndex !== -1) {
        const sourcesPart = buffer.slice(0, delimiterIndex).replace("\n", "");
        const sources = JSON.parse(sourcesPart).sources;
        buffer = buffer.slice(delimiterIndex + "<<<END_SOURCES>>>\n".length);
        sourcesParsed = true;

        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { ...updated[updated.length - 1], sources };
          return updated;
        });
      } else {
        continue;
      }
    }

    const chunkToAppend = buffer;
    buffer = "";

    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        text: updated[updated.length - 1].text + chunkToAppend,
      };
      return updated;
    });
  }
};

  return (
    <>
      <div className="stats-row">
        <button onClick={fetchStats}>Refresh Stats</button>
        {stats && (
          <div className="stats">
            <span>Requests: {stats.total_requests}</span>
            <span>Avg time: {stats.avg_duration_seconds}s</span>
            <span>Total cost: ${stats.total_estimated_cost_usd}</span>
            <span>Avg relevance: {stats.avg_retrieval_distance}</span>
          </div>
        )}
      </div>
      <div className="chat-container">
        <div className="upload-row">
          <input type="file" accept=".txt" onChange={handleUpload} />
          <span>{uploadStatus}</span>
        </div>
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              {m.text}
              {m.sources && m.sources.length > 0 && (
                <div className="sources">
                  {m.sources.map((s, j) => (
                    <div key={j} className="source-item">📄 {s.slice(0, 60)}...</div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="bubble bot">Thinking...</div>}
        </div>
        <div className="input-row">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Ask a question"
          />
          <button onClick={handleAsk}>Send</button>
        </div>
      </div>
    </>
  );
}

export default App;