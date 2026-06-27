from Agents.base_agent import BaseAgent
from Prompts.system_prompts import TESTING_PROMPT

class TestingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_prompt=TESTING_PROMPT,
            agent_name="Testing"
        )

    def generate_tests(self, code: str) -> str:
        prompt = f"""Generate a comprehensive test suite for this code:

```python
{code}
```

Generate:
1. Unit tests for every function
2. Integration tests
3. Edge case tests
4. Fixtures and mocks
5. Test configuration (conftest.py)

Use pytest framework."""
        return self.run(prompt, {"code": code})