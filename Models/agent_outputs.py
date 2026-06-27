from pydantic import BaseModel, Field
from typing import Optional, List

class RequirementOutput(BaseModel):
    functional: List[str] = Field(description="Functional requirements")
    non_functional: List[str] = Field(description="Non-functional requirements")
    constraints: List[str] = Field(default_factory=list)
    suggested_stack: List[str] = Field(description="Recommended technologies")
    complexity: str = Field(description="Low | Medium | High | Very High")
    estimated_hours: Optional[int] = None

class PlanOutput(BaseModel):
    milestones: List[str] = Field(description="List of milestones")
    file_structure: List[str] = Field(description="Project file structure")
    api_endpoints: Optional[List[str]] = None
    dependencies: List[str] = Field(description="Required packages")

class CodeOutput(BaseModel):
    code: str = Field(description="Generated code")
    language: str = Field(default="python")
    filename: str = Field(description="Suggested filename")
    dependencies: List[str] = Field(description="Required packages")
    description: str = Field(description="What the code does")

class BugFixOutput(BaseModel):
    original_code: str
    fixed_code: str
    bugs_found: List[str]
    explanation: str

class DocumentationOutput(BaseModel):
    readme: str
    docstrings: str
    api_docs: Optional[str] = None

class TestOutput(BaseModel):
    test_code: str
    framework: str = "pytest"
    test_cases: List[str]
    coverage_estimate: Optional[float] = None

class DeploymentOutput(BaseModel):
    dockerfile: str
    docker_compose: Optional[str] = None
    github_actions: Optional[str] = None
    env_vars: List[str] = Field(default_factory=list)

class WorkflowState(BaseModel):
    user_query: str
    session_id: str
    current_agent: str = "start"
    requirements: Optional[dict] = None
    plan: Optional[dict] = None
    generated_code: Optional[str] = None
    fixed_code: Optional[str] = None
    documentation: Optional[str] = None
    test_cases: Optional[str] = None
    deployment_config: Optional[str] = None
    error: Optional[str] = None
    is_complete: bool = False