from app.llm.base import LLMRequest
from app.llm.factory import create_llm_provider


class LLMAgent:
    """
    Purpose:
        Provide a provider-neutral natural-language reasoning interface.

    Responsibilities:
        - Preserve method contracts for summaries, question answering,
          comparisons, and market move explanations.
        - Keep LLM-provider details isolated from current API workflows.
        - Return graceful fallback responses when no provider is configured.

    Expected inputs:
        - Structured stock, company, news, market, or comparison context.
        - A user question when answering interactive research requests.

    Expected outputs:
        - Dictionaries containing natural-language responses, input context,
          and model metadata.

    Future expansion notes:
        - Add RAG context assembly, prompt templates, source citations, safety
          rules, and response evaluation before exposing this through APIs.
    """

    def __init__(self, provider=None):
        self.provider = provider or create_llm_provider()

    def get_status(self):
        return self.provider.get_status()

    def generate_summary(self, context=None):
        llm_response = self._generate(
            prompt="Generate a concise research-style summary from the provided context.",
            context=context or {},
        )

        response = {
            "task": "generate_summary",
            "context": context or {},
        }
        response.update(llm_response)
        return response

    def answer_question(self, question: str, context=None):
        llm_response = self._generate(
            prompt=question,
            context=context or {},
        )

        response = {
            "task": "answer_question",
            "question": question,
            "context": context or {},
        }
        response.update(llm_response)
        return response

    def compare_companies(self, companies=None, context=None):
        companies = companies or []
        llm_response = self._generate(
            prompt=f"Compare these companies for investment research: {companies}",
            context=context or {},
        )

        response = {
            "task": "compare_companies",
            "companies": companies,
            "context": context or {},
        }
        response.update(llm_response)
        return response

    def explain_market_move(self, market_context=None):
        llm_response = self._generate(
            prompt="Explain the likely drivers of this market move using the provided context.",
            context=market_context or {},
        )

        response = {
            "task": "explain_market_move",
            "market_context": market_context or {},
        }
        response.update(llm_response)
        return response

    def _generate(self, prompt: str, context=None):
        llm_response = self.provider.generate(
            LLMRequest(
                prompt=prompt,
                system_prompt=(
                    "You are an AI stock research assistant. Provide clear, "
                    "cautious, educational analysis and do not present content "
                    "as financial advice."
                ),
                context=context or {},
            )
        )

        return llm_response.to_dict()
