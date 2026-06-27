from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from Agents.requirement_analyzer import RequirementAnalyzerAgent
from Agents.planner import PlannerAgent
from Agents.code_generator import CodeGeneratorAgent
from Agents.bug_fixer import BugFixerAgent
from Agents.documentation import DocumentationAgent
from Agents.testing import TestingAgent
from Agents.deployment import DeploymentAgent
from loguru import logger
import concurrent.futures

class AgentState(TypedDict):
    user_query: str
    session_id: str
    current_agent: str
    requirements: Optional[str]
    plan: Optional[str]
    generated_code: Optional[str]
    fixed_code: Optional[str]
    documentation: Optional[str]
    test_cases: Optional[str]
    deployment_config: Optional[str]
    final_response: Optional[str]
    error: Optional[str]

req_agent = RequirementAnalyzerAgent()
plan_agent = PlannerAgent()
code_agent = CodeGeneratorAgent()
bug_agent = BugFixerAgent()
doc_agent = DocumentationAgent()
test_agent = TestingAgent()
deploy_agent = DeploymentAgent()

def requirement_node(state: AgentState) -> AgentState:
    logger.info("Running Requirement Analyzer...")
    result = req_agent.analyze(state["user_query"])
    return {**state, "requirements": result, "current_agent": "requirement_analyzer"}

def planner_node(state: AgentState) -> AgentState:
    logger.info("Running Planner...")
    result = plan_agent.plan(state["requirements"])
    return {**state, "plan": result, "current_agent": "planner"}

def code_generator_node(state: AgentState) -> AgentState:
    logger.info("Running Code Generator...")
    result = code_agent.generate(state["requirements"], state["plan"])
    return {**state, "generated_code": result, "current_agent": "code_generator"}

def parallel_node(state: AgentState) -> AgentState:
    """Run agents with small delays to avoid rate limits."""
    logger.info("Running parallel agents...")
    code = state.get("generated_code", "")
    requirements = state.get("requirements", "")
    import time

    # Small delay between each call to avoid rate limits
    fixed_code = bug_agent.fix(code)
    time.sleep(3)

    documentation = doc_agent.document(code, requirements)
    time.sleep(3)

    test_cases = test_agent.generate_tests(code)
    time.sleep(3)

    deployment_config = deploy_agent.generate_config(code, requirements)

    return {
        **state,
        "fixed_code": fixed_code,
        "documentation": documentation,
        "test_cases": test_cases,
        "deployment_config": deployment_config,
        "current_agent": "completed",
    }

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("requirement_analyzer", requirement_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("code_generator", code_generator_node)
    workflow.add_node("parallel_agents", parallel_node)

    workflow.set_entry_point("requirement_analyzer")
    workflow.add_edge("requirement_analyzer", "planner")
    workflow.add_edge("planner", "code_generator")
    workflow.add_edge("code_generator", "parallel_agents")
    workflow.add_edge("parallel_agents", END)

    return workflow.compile()

graph = build_graph()