from Agents.base_agent import BaseAgent
from Prompts.system_prompts import CODE_GENERATOR_PROMPT

class CodeGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=CODE_GENERATOR_PROMPT,
            agent_name="CodeGenerator"
        )

    def generate(self, requirements: str, plan: str) -> str:
        prompt = f"""Generate complete, production-ready code:

REQUIREMENTS:
{requirements}

IMPLEMENTATION PLAN:
{plan}

Generate:
1. Complete working Python code
2. All imports included
3. Error handling throughout
4. Docstrings for every function
5. Example usage at the bottom

Make it production-ready and well-commented."""
        return self.run(prompt, {"requirements": requirements, "plan": plan})