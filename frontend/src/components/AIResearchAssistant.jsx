import { useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../api/chatApi";

const QUICK_PROMPTS = [
  "What does this company do?",
  "Explain simply",
  "Main business areas",
  "What should I know?",
];

function devWarn(...args) {
  if (import.meta.env.DEV) {
    console.warn(...args);
  }
}

function AIResearchAssistant({ ticker }) {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [warning, setWarning] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [responseDetails, setResponseDetails] = useState(null);
  const requestControllerRef = useRef(null);
  const requestSequenceRef = useRef(0);

  useEffect(() => {
    const controllerRef = requestControllerRef;
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const submitQuestion = async (prompt) => {
    const normalizedQuestion = prompt?.trim() || "";

    if (!normalizedQuestion) {
      setError("Enter a question about this company.");
      return;
    }

    requestControllerRef.current?.abort();
    const controller = new AbortController();
    const requestId = requestSequenceRef.current + 1;
    requestSequenceRef.current = requestId;
    requestControllerRef.current = controller;

    setQuestion(normalizedQuestion);
    setSubmittedQuestion(normalizedQuestion);
    setAnswer("");
    setWarning("");
    setError("");
    setResponseDetails(null);
    setLoading(true);

    try {
      const response = await sendChatMessage({
        message: normalizedQuestion,
        ticker,
        mode: "auto",
        documents: [],
        signal: controller.signal,
      });

      if (requestSequenceRef.current !== requestId) {
        return;
      }

      setAnswer(typeof response?.answer === "string" ? response.answer : "");
      setWarning(
        typeof response?.warning === "string" ? response.warning : ""
      );
      setResponseDetails({
        mode: response?.mode || "",
        ticker: response?.ticker || ticker,
      });
    } catch (requestError) {
      if (
        requestError?.name === "AbortError" ||
        requestSequenceRef.current !== requestId
      ) {
        return;
      }

      devWarn("AI Research Assistant request failed:", requestError);
      setError("The AI Research Assistant is temporarily unavailable.");
    } finally {
      if (requestSequenceRef.current === requestId) {
        requestControllerRef.current = null;
        setLoading(false);
      }
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    submitQuestion(question);
  };

  return (
    <section className="ai-assistant-card">
      <div className="ai-assistant-header">
        <div>
          <p className="ai-assistant-eyebrow">AI Research</p>
          <h2>AI Research Assistant</h2>
          <p className="ai-assistant-subtitle">
            Ask questions about this company.
          </p>
        </div>

        <span className="ai-assistant-status">Single-turn</span>
      </div>

      <div className="ai-assistant-quick-prompts">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            disabled={loading}
            onClick={() => submitQuestion(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>

      <form className="ai-assistant-form" onSubmit={handleSubmit}>
        <label className="ai-assistant-label" htmlFor="ai-assistant-question">
          Your question
        </label>
        <div className="ai-assistant-input-row">
          <input
            id="ai-assistant-question"
            type="text"
            value={question}
            disabled={loading}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about this company…"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Thinking…" : "Ask"}
          </button>
        </div>
      </form>

      <div className="ai-assistant-feedback" aria-live="polite">
        {error && <p className="ai-assistant-error">{error}</p>}

        {warning && <p className="ai-assistant-warning">{warning}</p>}

        {submittedQuestion && (answer || loading) && (
          <div className="ai-assistant-result">
            <p className="ai-assistant-question-label">Latest question</p>
            <p className="ai-assistant-question">{submittedQuestion}</p>

            {loading ? (
              <p className="ai-assistant-thinking">Thinking…</p>
            ) : (
              <p className="ai-assistant-answer">{answer}</p>
            )}

            {!loading && responseDetails && (
              <div className="ai-assistant-metadata">
                {responseDetails.mode && (
                  <span>Mode: {responseDetails.mode}</span>
                )}
                {responseDetails.ticker && (
                  <span>Ticker: {responseDetails.ticker}</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}

export default AIResearchAssistant;
