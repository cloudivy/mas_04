"""
Basic tests for the multi-agent framework.
Run: pytest tests/ -v
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from memory.memory_store import MemoryStore
from rag.rag_store import RAGStore
from tools.tool_registry import ToolRegistry
from eval.agent_metrics import AgentMetrics


def test_memory_store_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("memory.memory_store.MEMORY_DIR", tmp_path)
    m = MemoryStore(namespace="test")
    m.store("key1", "hello world about Python", tags=["python"])
    results = m.retrieve("Python programming", top_k=1)
    assert len(results) == 1
    assert "hello world" in results[0]


def test_rag_store_add_retrieve(tmp_path, monkeypatch):
    monkeypatch.setattr("rag.rag_store.RAG_DIR", tmp_path)
    store = RAGStore(collection="test")
    store.add_document("FastAPI Guide", "FastAPI is a modern Python web framework for APIs")
    results = store.retrieve("Python web API")
    assert len(results) >= 1
    assert results[0]["title"] == "FastAPI Guide"


def test_tool_registry_builtins():
    reg = ToolRegistry()
    tools = reg.list_tools()
    names = [t["name"] for t in tools]
    assert "calculator" in names
    assert "timestamp" in names
    result = reg.invoke("calculator", expression="2 + 2")
    assert result == "4"


def test_agent_metrics_asi(tmp_path, monkeypatch):
    monkeypatch.setattr("eval.agent_metrics.EVAL_DIR", tmp_path)
    m = AgentMetrics(agent_id="test_agent")
    scores = m.record_run(
        task="build a recommendation engine",
        output="A recommendation engine uses collaborative filtering and content-based methods.",
        context="",
        elapsed=1.2,
        mode="simulated",
    )
    assert "asi" in scores
    assert 0 <= scores["asi"] <= 100


def test_agent_metrics_history(tmp_path, monkeypatch):
    monkeypatch.setattr("eval.agent_metrics.EVAL_DIR", tmp_path)
    m = AgentMetrics(agent_id="hist_agent")
    for i in range(3):
        m.record_run(task=f"task {i}", output=f"output for task {i}", context="", elapsed=0.5, mode="sim")
    history = m.get_history(10)
    assert len(history) == 3
