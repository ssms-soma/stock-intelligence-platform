import { useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../api/chatApi";
import {
  askUploadedDocument,
  DocumentApiError,
  uploadDocument,
} from "../api/documentApi";

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
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedDocument, setUploadedDocument] = useState(null);
  const [activeMode, setActiveMode] = useState("company");
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadWarning, setUploadWarning] = useState("");
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [warning, setWarning] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const [responseDetails, setResponseDetails] = useState(null);
  const fileInputRef = useRef(null);
  const uploadControllerRef = useRef(null);
  const uploadSequenceRef = useRef(0);
  const requestControllerRef = useRef(null);
  const requestSequenceRef = useRef(0);

  useEffect(() => {
    const uploadController = uploadControllerRef;
    const requestController = requestControllerRef;

    return () => {
      uploadController.current?.abort();
      requestController.current?.abort();
    };
  }, []);

  const clearAnswerState = () => {
    setSubmittedQuestion("");
    setAnswer("");
    setWarning("");
    setError("");
    setSources([]);
    setResponseDetails(null);
  };

  const cancelAnswerRequest = () => {
    requestControllerRef.current?.abort();
    requestControllerRef.current = null;
    requestSequenceRef.current += 1;
    setLoading(false);
  };

  const handleModeChange = (nextMode) => {
    if (nextMode === "document" && !uploadedDocument?.document_id) {
      return;
    }

    cancelAnswerRequest();
    setActiveMode(nextMode);
    clearAnswerState();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    const filename = file?.name?.toLowerCase() || "";

    uploadControllerRef.current?.abort();
    uploadControllerRef.current = null;
    uploadSequenceRef.current += 1;
    setUploadLoading(false);
    setUploadError("");
    setUploadWarning("");
    setUploadedDocument(null);
    setActiveMode("company");
    cancelAnswerRequest();
    clearAnswerState();

    if (
      file &&
      !filename.endsWith(".txt") &&
      !filename.endsWith(".md") &&
      !filename.endsWith(".pdf")
    ) {
      setSelectedFile(null);
      setUploadError("Upload a .txt, .md, or .pdf file.");
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Upload a .txt, .md, or .pdf file.");
      return;
    }

    uploadControllerRef.current?.abort();
    const controller = new AbortController();
    const uploadId = uploadSequenceRef.current + 1;
    uploadSequenceRef.current = uploadId;
    uploadControllerRef.current = controller;

    setUploadLoading(true);
    setUploadError("");
    setUploadWarning("");

    try {
      const response = await uploadDocument({
        file: selectedFile,
        signal: controller.signal,
      });

      if (uploadSequenceRef.current !== uploadId) {
        return;
      }

      const isIndexed =
        response?.status === "indexed" &&
        typeof response?.document_id === "string" &&
        Boolean(response.document_id);

      if (!isIndexed) {
        setUploadedDocument(null);
        setActiveMode("company");
        setUploadWarning(
          typeof response?.warning === "string" && response.warning
            ? response.warning
            : "Could not upload this document."
        );
        return;
      }

      setUploadedDocument({
        document_id: response.document_id,
        title:
          typeof response?.title === "string" && response.title
            ? response.title
            : selectedFile.name,
        chunks_indexed: Number.isFinite(response?.chunks_indexed)
          ? response.chunks_indexed
          : 0,
        pages_indexed: Number.isFinite(response?.pages_indexed)
          ? response.pages_indexed
          : null,
      });
      setUploadWarning(
        typeof response?.warning === "string" ? response.warning : ""
      );
      cancelAnswerRequest();
      clearAnswerState();
      setActiveMode("document");
    } catch (uploadRequestError) {
      if (
        uploadRequestError?.name === "AbortError" ||
        uploadSequenceRef.current !== uploadId
      ) {
        return;
      }

      devWarn("Document upload failed:", uploadRequestError);
      setUploadError(
        uploadRequestError instanceof DocumentApiError
          ? uploadRequestError.message
          : "Document upload is temporarily unavailable."
      );
    } finally {
      if (uploadSequenceRef.current === uploadId) {
        uploadControllerRef.current = null;
        setUploadLoading(false);
      }
    }
  };

  const submitQuestion = async (prompt) => {
    const normalizedQuestion = prompt?.trim() || "";
    const requestMode = activeMode;
    const documentId = uploadedDocument?.document_id;

    if (!normalizedQuestion) {
      setError(
        requestMode === "document"
          ? "Enter a question about this document."
          : "Enter a question about this company."
      );
      return;
    }

    if (requestMode === "document" && !documentId) {
      setError("Upload a document before asking a document question.");
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
    setSources([]);
    setResponseDetails(null);
    setLoading(true);

    try {
      const response =
        requestMode === "document"
          ? await askUploadedDocument({
              documentId,
              question: normalizedQuestion,
              topK: 5,
              signal: controller.signal,
            })
          : await sendChatMessage({
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

      if (requestMode === "document") {
        setSources(Array.isArray(response?.sources) ? response.sources : []);
        setResponseDetails({
          mode: response?.metadata?.mode || "uploaded_document_rag",
          title: uploadedDocument?.title || "",
        });
      } else {
        setResponseDetails({
          mode: response?.mode || "",
          ticker: response?.ticker || ticker,
        });
      }
    } catch (requestError) {
      if (
        requestError?.name === "AbortError" ||
        requestSequenceRef.current !== requestId
      ) {
        return;
      }

      devWarn("AI Research Assistant request failed:", requestError);

      if (
        requestMode === "document" &&
        requestError instanceof DocumentApiError &&
        requestError.status === 404
      ) {
        setUploadedDocument(null);
        setSelectedFile(null);
        setUploadWarning("");
        setActiveMode("company");
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        setError(
          "This uploaded document is no longer available. Please upload it again."
        );
      } else {
        setError("The AI Research Assistant is temporarily unavailable.");
      }
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

  const controlsDisabled = loading || uploadLoading;

  return (
    <section className="ai-assistant-card">
      <div className="ai-assistant-header">
        <div>
          <p className="ai-assistant-eyebrow">AI Research</p>
          <h2>AI Research Assistant</h2>
          <p className="ai-assistant-subtitle">
            Ask questions about this company or an uploaded document.
          </p>
        </div>

        <span className="ai-assistant-status">Single-turn</span>
      </div>

      <div className="ai-assistant-document-section">
        <div className="ai-assistant-document-heading">
          <div>
            <p className="ai-assistant-document-title">Document Q&amp;A</p>
            <p className="ai-assistant-document-help">
              Upload a .txt, .md, or text-based .pdf file.
            </p>
            <p className="ai-assistant-document-help">
              Text-based PDFs only. Scanned PDFs are not supported yet.
            </p>
          </div>
        </div>

        <div className="ai-assistant-upload-row">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.pdf,text/plain,text/markdown,application/pdf"
            disabled={controlsDisabled}
            onChange={handleFileChange}
          />
          <button
            type="button"
            disabled={!selectedFile || controlsDisabled}
            onClick={handleUpload}
          >
            {uploadLoading ? "Uploading and indexing..." : "Upload document"}
          </button>
        </div>

        {selectedFile && !uploadedDocument && !uploadLoading && (
          <p className="ai-assistant-selected-file">
            Selected: {selectedFile.name}
          </p>
        )}

        {uploadError && (
          <p className="ai-assistant-error ai-assistant-upload-message">
            {uploadError}
          </p>
        )}

        {uploadedDocument && (
          <div className="ai-assistant-document-summary">
            <div>
              <span className="ai-assistant-document-name">
                {uploadedDocument.title}
              </span>
              <span className="ai-assistant-document-count">
                {uploadedDocument.pages_indexed !== null && (
                  <>
                    {uploadedDocument.pages_indexed}{" "}
                    {uploadedDocument.pages_indexed === 1 ? "page" : "pages"}
                    {" \u00b7 "}
                  </>
                )}
                {uploadedDocument.chunks_indexed}{" "}
                {uploadedDocument.chunks_indexed === 1 ? "chunk" : "chunks"} indexed
              </span>
            </div>
          </div>
        )}

        {uploadWarning && (
          <p className="ai-assistant-warning ai-assistant-upload-message">
            {uploadWarning}
          </p>
        )}
      </div>

      <div className="ai-assistant-context-switch" aria-label="Question context">
        <button
          type="button"
          className={activeMode === "company" ? "is-active" : ""}
          disabled={controlsDisabled}
          aria-pressed={activeMode === "company"}
          onClick={() => handleModeChange("company")}
        >
          Ask company
        </button>
        <button
          type="button"
          className={activeMode === "document" ? "is-active" : ""}
          disabled={controlsDisabled || !uploadedDocument?.document_id}
          aria-pressed={activeMode === "document"}
          onClick={() => handleModeChange("document")}
        >
          Ask document
        </button>
      </div>

      <div className="ai-assistant-quick-prompts">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            disabled={controlsDisabled}
            onClick={() => submitQuestion(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>

      <form className="ai-assistant-form" onSubmit={handleSubmit}>
        <label className="ai-assistant-label" htmlFor="ai-assistant-question">
          {activeMode === "document"
            ? "Your document question"
            : "Your company question"}
        </label>
        <div className="ai-assistant-input-row">
          <input
            id="ai-assistant-question"
            type="text"
            value={question}
            disabled={controlsDisabled}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={
              activeMode === "document"
                ? "Ask about the uploaded document..."
                : "Ask about this company..."
            }
          />
          <button type="submit" disabled={controlsDisabled}>
            {loading ? "Thinking..." : "Ask"}
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
              <p className="ai-assistant-thinking">Thinking...</p>
            ) : (
              <p className="ai-assistant-answer">{answer}</p>
            )}

            {!loading && sources.length > 0 && (
              <div className="ai-assistant-sources">
                <p className="ai-assistant-question-label">Sources</p>
                <ul>
                  {sources.map((source, index) => {
                    const score = Number(source?.score);
                    const page = Number(source?.page);
                    const hasPage =
                      source?.page !== null &&
                      source?.page !== undefined &&
                      Number.isFinite(page);
                    return (
                      <li key={source?.chunk_id || `${source?.title}-${index}`}>
                        <span>{source?.title || "Uploaded document"}</span>
                        {hasPage && <span>Page {page}</span>}
                        {source?.chunk_id && <span>{source.chunk_id}</span>}
                        {Number.isFinite(score) && (
                          <span>Score: {score.toFixed(3)}</span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}

            {!loading && responseDetails && (
              <div className="ai-assistant-metadata">
                {responseDetails.mode && (
                  <span>
                    Context:{" "}
                    {responseDetails.mode === "uploaded_document_rag"
                      ? "Document"
                      : "Company"}
                  </span>
                )}
                {responseDetails.ticker && (
                  <span>Ticker: {responseDetails.ticker}</span>
                )}
                {responseDetails.title && (
                  <span>Document: {responseDetails.title}</span>
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
