from app.agents.llm_agent import LLMAgent


class LLMService:
    def __init__(self):
        self.llm_agent = LLMAgent()

    def get_status(self):
        return self.llm_agent.get_status()

    def test_prompt(self, prompt: str):
        return self.llm_agent.answer_question(
            question=prompt,
            context={
                "purpose": "LLM configuration test",
            },
        )
