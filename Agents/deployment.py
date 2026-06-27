from Agents.base_agent import BaseAgent
from Prompts.system_prompts import DEPLOYMENT_PROMPT

class DeploymentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=DEPLOYMENT_PROMPT,
            agent_name="Deployment"
        )

    def generate_config(self, code: str, requirements: str) -> str:
        prompt = f"""Generate complete deployment configuration:

PROJECT REQUIREMENTS:
{requirements}

Generate:
1. Dockerfile (multi-stage)
2. docker-compose.yml
3. GitHub Actions CI/CD (.github/workflows/ci.yml)
4. Environment variables list (.env.example)
5. Deployment instructions"""
        return self.run(prompt, {"requirements": requirements})