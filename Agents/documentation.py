from Agents.base_agent import BaseAgent
from Prompts.system_prompts import DOCUMENTATION_PROMPT

class DocumentationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=DOCUMENTATION_PROMPT,
            agent_name="Documentation"
        )

    def document(self, code: str, requirements: str) -> str:
        prompt = f"""Generate complete documentation for this code:

CODE:
{code}

REQUIREMENTS:
{requirements}

Generate:
1. README.md with badges and setup instructions
2. API documentation
3. Function docstrings
4. Usage examples
5. Architecture overview"""
        return self.run(prompt, {"code": code})