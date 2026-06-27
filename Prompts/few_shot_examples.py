REQUIREMENT_FEW_SHOTS = """
=== FEW-SHOT EXAMPLES ===

Example 1:
Input: "Build a REST API for a todo app"
Output:
{
  "functional": ["CRUD endpoints for todos", "User authentication", "Filtering by status"],
  "non_functional": ["Response time < 200ms", "JWT auth", "PostgreSQL storage"],
  "stack": ["FastAPI", "PostgreSQL", "Redis", "Docker"],
  "complexity": "Medium"
}

Example 2:
Input: "Add rate limiting to existing FastAPI service"
Output:
{
  "functional": ["Limit requests per IP per minute", "Return 429 with Retry-After header"],
  "non_functional": ["<1ms overhead", "Redis-backed sliding window"],
  "stack": ["slowapi", "Redis", "FastAPI middleware"],
  "complexity": "Low"
}
=== END EXAMPLES ===
"""