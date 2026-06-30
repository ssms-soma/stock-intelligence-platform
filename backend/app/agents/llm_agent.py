class LLMAgent:
    """
    Purpose:
        Define the future natural-language reasoning interface without
        integrating an external language model yet.

    Responsibilities:
        - Reserve method contracts for summaries, question answering,
          comparisons, and market move explanations.
        - Return deterministic placeholder responses during Phase 2.
        - Keep all LLM-provider details isolated from current API workflows.

    Expected inputs:
        - Structured stock, company, news, market, or comparison context.
        - A user question when answering interactive research requests.

    Expected outputs:
        - Dictionaries containing placeholder natural-language responses,
          input context, and model metadata.

    Future expansion notes:
        - Integrate OpenAI, Gemini, Ollama, or another model provider later.
        - Add RAG context assembly, prompt templates, source citations, safety
          rules, and response evaluation before exposing this through APIs.
    """

    MODEL_STATUS = "not_integrated"

    def generate_summary(self, context=None):
        # TODO: Connect to an LLM with RAG-backed context in a later phase.
        return {
            "task": "generate_summary",
            "response": "LLM summary generation is not integrated yet.",
            "context": context or {},
            "model_status": self.MODEL_STATUS,
        }

    def answer_question(self, question: str, context=None):
        # TODO: Route the question through a prompt template and grounded sources.
        return {
            "task": "answer_question",
            "question": question,
            "response": "LLM question answering is not integrated yet.",
            "context": context or {},
            "model_status": self.MODEL_STATUS,
        }

    def compare_companies(self, companies=None, context=None):
        # TODO: Generate sourced company comparisons after model integration.
        return {
            "task": "compare_companies",
            "companies": companies or [],
            "response": "LLM company comparison is not integrated yet.",
            "context": context or {},
            "model_status": self.MODEL_STATUS,
        }

    def explain_market_move(self, market_context=None):
        # TODO: Combine market data, news, and retrieval context for explanations.
        return {
            "task": "explain_market_move",
            "response": "LLM market move explanation is not integrated yet.",
            "market_context": market_context or {},
            "model_status": self.MODEL_STATUS,
        }
