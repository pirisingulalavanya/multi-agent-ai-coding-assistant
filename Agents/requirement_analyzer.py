from Agents.base_agent import BaseAgent
from Prompts.system_prompts import REQUIREMENT_ANALYZER_PROMPT

class RequirementAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=REQUIREMENT_ANALYZER_PROMPT,
            agent_name="RequirementAnalyzer"
        )

    def analyze(self, user_query: str) -> str:
        prompt = f"""Analyze this software request and extract all requirements:

Request: {user_query}

Provide:
1. FUNCTIONAL REQUIREMENTS (bullet points)
2. NON-FUNCTIONAL REQUIREMENTS (performance, security, scalability)
3. CONSTRAINTS & ASSUMPTIONS
4. RECOMMENDED TECH STACK
5. COMPLEXITY: Low/Medium/High
6. ESTIMATED HOURS

Think step by step before answering."""
        return self.run(prompt)