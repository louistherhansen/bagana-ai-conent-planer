"""
BAGANA AI — Crew run entrypoint (stub).
SAD §2, §4: Load agents and tasks from config/agents.yaml, config/tasks.yaml;
orchestrate crew; bind tools in code. Backend epic implements kickoff and tools.
"""
from pathlib import Path

# Config paths per SAD
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
AGENTS_PATH = CONFIG_DIR / "agents.yaml"
TASKS_PATH = CONFIG_DIR / "tasks.yaml"


def load_config():
    """Load agent and task config from YAML. Backend epic: parse and build Crew."""
    if not AGENTS_PATH.exists() or not TASKS_PATH.exists():
        raise FileNotFoundError(
            f"Config missing: {AGENTS_PATH} / {TASKS_PATH}. Run *setup-project."
        )
    # Backend epic: use PyYAML or similar to load; build CrewAI Crew from config
    return {"agents_path": str(AGENTS_PATH), "tasks_path": str(TASKS_PATH)}


def kickoff(inputs: dict) -> dict:
    """
    Placeholder for crew.kickoff(inputs). Backend epic: build crew from config,
    bind tools, run sequential tasks, return/output artifacts per SAD.
    """
    load_config()
    # Backend epic: Crew().kickoff(inputs); stream if needed; write Audit
    return {"status": "stub", "message": "Implement in backend epic (*develop-be)."}
