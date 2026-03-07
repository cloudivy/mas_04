"""
Agent Registry — single source of truth for all agents in the framework.

To add a new agent:
  1. Create agents/my_agent.py subclassing BaseAgent
  2. Import it here and add to REGISTRY
  3. Restart the API — it's automatically available
"""
from agents.base_agent import BaseAgent
from agents.builtin.orchestrator_agent import OrchestratorAgent
from agents.builtin.researcher_agent import ResearcherAgent
from agents.builtin.planner_agent import PlannerAgent
from agents.builtin.executor_agent import ExecutorAgent
from agents.builtin.critic_agent import CriticAgent


# ── Registry: maps agent_id → class ──────────────────────────────────────────
REGISTRY: dict[str, type[BaseAgent]] = {
    "orchestrator": OrchestratorAgent,
    "researcher":   ResearcherAgent,
    "planner":      PlannerAgent,
    "executor":     ExecutorAgent,
    "critic":       CriticAgent,
    # Add your custom agents here:
    # "my_agent": MyAgent,
}

# Default sequential pipeline order
DEFAULT_PIPELINE = ["orchestrator", "researcher", "planner", "executor", "critic"]


def get_agent(agent_id: str, api_key: str = "", simulate: bool = False) -> BaseAgent:
    if agent_id not in REGISTRY:
        raise ValueError(f"Unknown agent '{agent_id}'. Available: {list(REGISTRY.keys())}")
    return REGISTRY[agent_id](api_key=api_key, simulate=simulate)


def list_agents() -> list[dict]:
    return [
        {
            "id": aid,
            "name": cls.name,
            "role": cls.role,
            "icon": cls.icon,
            "color": cls.color,
        }
        for aid, cls in REGISTRY.items()
    ]
