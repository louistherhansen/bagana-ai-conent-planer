"""
BAGANA AI — Crew run entrypoint.
SAD §2, §4: Load agents and tasks from config/agents.yaml, config/tasks.yaml;
orchestrate crew; bind tools in code.
"""
from pathlib import Path
from datetime import datetime

import yaml
from crewai import Agent, Task, Crew

from crew.tools import plan_schema_validator, sentiment_schema_validator, trend_schema_validator

# Backlog stubs: crew.stubs (SentimentAPIClient, TrendAPIClient, build_report_summarizer_agent_stub, etc.)

# Config paths per SAD
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
AGENTS_PATH = CONFIG_DIR / "agents.yaml"
TASKS_PATH = CONFIG_DIR / "tasks.yaml"
LOGS_DIR = Path(__file__).resolve().parent.parent / "project-context" / "2.build" / "logs"

# Agent ID -> tools mapping (adapter: bind only tools needed per task)
AGENT_TOOLS = {
    "content_planner": [plan_schema_validator],
    "sentiment_analyst": [sentiment_schema_validator],
    "trend_researcher": [trend_schema_validator],
}

# Valid Agent constructor params (filter YAML to avoid passing invalid fields)
AGENT_PARAMS = {
    "role", "goal", "backstory", "llm", "allow_delegation", "verbose",
    "max_iter", "max_execution_time", "max_retry_limit", "respect_context_window",
    "tools",
}

# Valid Task constructor params
TASK_PARAMS = {
    "name", "description", "expected_output", "agent", "context",
    "output_file", "create_directory",
}


def _load_yaml(path: Path) -> dict:
    """Load and parse YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Config missing: {path}. Run *setup-project.")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_agent(agent_id: str, config: dict) -> Agent:
    """Build CrewAI Agent from YAML config. Bind tools in code per adapter."""
    params = {k: v for k, v in config.items() if k in AGENT_PARAMS}
    params.pop("tools", None)  # We bind tools in code
    tools = AGENT_TOOLS.get(agent_id, [])
    params["tools"] = tools
    return Agent(**params)


def _build_task(
    task_id: str,
    config: dict,
    agents: dict[str, Agent],
    task_refs: dict[str, Task],
) -> Task:
    """Build CrewAI Task from YAML config. Resolve context_from to Task refs."""
    agent_ref = config.get("agent")
    if agent_ref not in agents:
        raise ValueError(f"Task {task_id}: unknown agent {agent_ref}")
    agent = agents[agent_ref]

    params = {k: v for k, v in config.items() if k in TASK_PARAMS}
    params["agent"] = agent
    params.pop("context_from", None)

    context_from = config.get("context_from", [])
    if context_from:
        params["context"] = [task_refs[cid] for cid in context_from if cid in task_refs]
    elif "context" not in params:
        params["context"] = []

    return Task(**params)


def load_config() -> tuple[dict, dict]:
    """Load agent and task config from YAML."""
    agents_data = _load_yaml(AGENTS_PATH)
    tasks_data = _load_yaml(TASKS_PATH)
    return agents_data, tasks_data


def build_crew() -> Crew:
    """
    Build Crew from YAML config.
    Sequential flow: plan_content → analyze_sentiment, research_trends (both use plan output).
    """
    agents_data, tasks_data = load_config()
    agents_cfg = agents_data.get("agents", {})
    tasks_cfg = tasks_data.get("tasks", {})

    # Validate tool presence per adapter
    for aid in agents_cfg:
        if aid not in AGENT_TOOLS and agents_cfg[aid].get("tools"):
            raise ValueError(f"Agent {aid}: tools declared but not bound. Add to AGENT_TOOLS in run.py.")

    # Build agents
    agents = {aid: _build_agent(aid, cfg) for aid, cfg in agents_cfg.items()}

    # Build tasks in dependency order (plan first, then sentiment and trends)
    task_refs: dict[str, Task] = {}
    tasks: list[Task] = []

    for tid in ["plan_content", "analyze_sentiment", "research_trends"]:
        if tid not in tasks_cfg:
            continue
        t = _build_task(tid, tasks_cfg[tid], agents, task_refs)
        task_refs[tid] = t
        tasks.append(t)

    return Crew(agents=list(agents.values()), tasks=tasks, verbose=False, step_callback=_step_callback)


def _step_callback(step: object) -> None:
    """Write step to Trace Log per adapter Memory and Logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "trace.log"
    ts = datetime.utcnow().isoformat() + "Z"
    info = getattr(step, "__dict__", {}) if hasattr(step, "__dict__") else (step if isinstance(step, dict) else {})
    agent = info.get("agent", getattr(step, "agent", "?"))
    task = info.get("task", getattr(step, "task", "?"))
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] step: {agent} | {task}\n")


def kickoff(inputs: dict | None = None) -> dict:
    """
    Run crew.kickoff(inputs). Returns structured result for API/Integration epic.
    inputs: { user_input: str, campaign_context?: str, ... } for task interpolation.
    """
    inputs = inputs or {}
    if "user_input" not in inputs:
        inputs["user_input"] = inputs.get("message", inputs.get("campaign_context", "No context provided."))

    crew = build_crew()
    if crew.step_callback is None:
        crew.step_callback = _step_callback

    try:
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        return {"status": "error", "error": str(e)}

    # Build JSON-serializable output for API (CrewOutput has raw, tasks_output)
    raw_output = getattr(result, "raw", str(result))
    task_outputs = getattr(result, "tasks_output", [])
    outputs_list = [
        {"task": getattr(to, "name", None) or getattr(to, "description", f"task_{i}")[:50], "output": str(getattr(to, "raw", to))}
        for i, to in enumerate(task_outputs)
    ]

    return {
        "status": "complete",
        "output": raw_output,
        "task_outputs": outputs_list,
    }


if __name__ == "__main__":
    """CLI entrypoint. Usage: python -m crew.run [message] | python -m crew.run --stdin (reads JSON from stdin, writes JSON to stdout for API)."""
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--stdin":
        # API mode: read JSON from stdin, write JSON to stdout
        try:
            payload = json.load(sys.stdin)
            result = kickoff(payload)
            json.dump(result, sys.stdout, indent=2)
        except Exception as e:
            json.dump({"status": "error", "error": str(e)}, sys.stdout, indent=2)
            sys.exit(1)
    else:
        # CLI mode: human-readable output
        msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Create a content plan for a summer campaign with 3 talents."
        result = kickoff({"user_input": msg})
        print("Status:", result.get("status"))
        if result.get("error"):
            print("Error:", result["error"])
        else:
            out = result.get("output", "")
            print("Output:", out[:500] + "..." if len(str(out)) > 500 else out)
