from openai import AsyncOpenAI

from app.agent.models import AgentDecision
from app.agent.prompts import SYSTEM_PROMPT, build_user_prompt


class OpenAIPlanner:
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def decide(self, goal: str, observation: dict) -> AgentDecision:
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(goal, observation)},
            ],
            response_format=AgentDecision,
        )
        message = response.choices[0].message
        if message.parsed is None:
            raise RuntimeError("LLM returned no structured decision")
        return message.parsed
