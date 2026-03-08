"""Agent prompt templates.

Each role module exposes compose_prompt(task, source) -> str.
"""

from . import developer, dev_lead, qa, qa_lead, reviewer, analyst

_ROLE_MODULES = {
    "developer": developer,
    "dev-lead": dev_lead,
    "qa": qa,
    "qa-lead": qa_lead,
    "reviewer": reviewer,
    "analyst": analyst,
}


def compose_prompt(task: str, agent_role: str = "developer", source: str = "direct") -> str:
    """Compose a complete prompt for the given agent role.

    Args:
        task: Task description or Linear issue ID
        agent_role: Agent role name (developer, qa, reviewer, analyst)
        source: "linear" or "direct"

    Returns:
        Complete prompt string with role, context, guidance, and task
    """
    module = _ROLE_MODULES.get(agent_role, developer)
    return module.compose_prompt(task, source)
