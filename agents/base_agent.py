"""
Base Agent — all agents in the framework extend this class.
To add a new agent: subclass BaseAgent, implement `system_prompt` and optionally `tools`.
"""
from __future__ import annotations
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from memory.memory_store import MemoryStore
from tools.tool_registry import ToolRegistry
from eval.agent_metrics import AgentMetrics


@dataclass
class AgentMessage:
    role: str           # "user" | "assistant" | "system"
    content: str
    agent_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    agent_id: str
    agent_name: str
    output: str
    messages: list[AgentMessage]
    metrics: dict
    tool_calls: list[dict]
    elapsed_s: float
    success: bool
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Extend this to create a new agent. Minimum required: define `agent_id`, `name`, `role`.
    Override `system_prompt` for custom behavior.
    Override `tools` to register agent-specific tools.
    """

    agent_id: str = "base"
    name: str = "Base Agent"
    role: str = "Generic agent"
    icon: str = "◎"
    color: str = "#888888"

    def __init__(self, api_key: str = "", simulate: bool = False):
        self.api_key = api_key
        self.simulate = simulate
        self.memory = MemoryStore(namespace=self.agent_id)
        self.tool_registry = ToolRegistry()
        self.metrics = AgentMetrics(agent_id=self.agent_id)
        self._register_tools()

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Define this agent's persona and instructions."""
        ...

    def _register_tools(self):
        """Override to register agent-specific tools."""
        pass

    def _simulated_response(self, task: str, context: str) -> str:
        """Fallback simulation when no API key is available."""
        return (
            f"[SIMULATED] {self.name} processed: '{task[:60]}...'\n\n"
            f"Role: {self.role}\n"
            f"Context tokens received: {len(context.split())}\n"
            f"Output: Placeholder response — add API key for real LLM calls."
        )

    def _call_api(self, task: str, context: str) -> str:
        """Call OpenAI API. Raises on failure so caller can fallback."""
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        user_content = f"Task: {task}"
        if context.strip():
            user_content = f"Task: {task}\n\nContext from prior agents:\n{context}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",   # cheap & fast — swap to gpt-4o for higher quality
            max_tokens=600,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": user_content},
            ],
        )
        return response.choices[0].message.content

    def run(self, task: str, context: str = "") -> AgentResult:
        """Execute this agent. Called by the orchestrator."""
        start = time.time()
        messages: list[AgentMessage] = []
        tool_calls: list[dict] = []
        error = None

        # Load relevant memories
        memories = self.memory.retrieve(query=task, top_k=3)
        if memories:
            context += f"\n\n[Memory]\n" + "\n".join(f"- {m}" for m in memories)

        try:
            if self.simulate or not self.api_key:
                output = self._simulated_response(task, context)
                mode = "simulated"
            else:
                try:
                    output = self._call_api(task, context)
                    mode = "api"
                except Exception as e:
                    output = self._simulated_response(task, context)
                    output += f"\n\n[API fallback: {e}]"
                    mode = "fallback"
                    error = str(e)

            # Store output in memory
            self.memory.store(key=f"run_{uuid.uuid4().hex[:8]}", value=output, tags=[task[:40]])

            # Record metrics
            elapsed = time.time() - start
            metrics = self.metrics.record_run(
                task=task, output=output, context=context, elapsed=elapsed, mode=mode
            )

            messages.append(AgentMessage(role="assistant", content=output, agent_id=self.agent_id))
            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                output=output,
                messages=messages,
                metrics=metrics,
                tool_calls=tool_calls,
                elapsed_s=elapsed,
                success=True,
                error=error,
            )
        except Exception as e:
            elapsed = time.time() - start
            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                output="",
                messages=messages,
                metrics={},
                tool_calls=tool_calls,
                elapsed_s=elapsed,
                success=False,
                error=str(e),
            )
