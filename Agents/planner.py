from Agents.base_agent import BaseAgent
from Prompts.system_prompts import PLANNER_PROMPT

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=PLANNER_PROMPT,
            agent_name="Planner"
        )

    def plan(self, requirements: str) -> str:
        prompt = f"""Create a detailed implementation plan based on these requirements:

{requirements}

Provide:
1. PROJECT MILESTONES (ordered list)
2. FILE/FOLDER STRUCTURE (tree format)
3. API ENDPOINTS (if applicable)
4. DEPENDENCIES (pip packages)
5. DEVELOPMENT ROADMAP (step by step)"""
        return self.run(prompt, {"requirements": requirements})