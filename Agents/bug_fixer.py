from Agents.base_agent import BaseAgent
from Prompts.system_prompts import BUG_FIXER_PROMPT

class BugFixerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=BUG_FIXER_PROMPT,
            agent_name="BugFixer"
        )

    def fix(self, code: str) -> str:
        prompt = f"""Review and fix all bugs in this code:

```python
{code}
```

Provide:
1. LIST OF BUGS FOUND
2. ROOT CAUSE of each bug
3. COMPLETE FIXED CODE
4. EXPLANATION of changes made"""
        return self.run(prompt, {"code": code})