import { useEffect, useState } from "react";

function App() {
  const [backendMessage, setBackendMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendMessage(data.message);
      })
      .catch(() => {
        setBackendMessage("Backend connection failed");
      });
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>AI Stock Intelligence Platform</h1>

      <h2>Backend Status</h2>

      <p>{backendMessage}</p>
    </div>
  );
}

export default App;