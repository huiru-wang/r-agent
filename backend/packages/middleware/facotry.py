from typing import TYPE_CHECKING, List

from langchain.agents.middleware import AgentMiddleware
from langchain_core.runnables import RunnableConfig
from packages.middleware.title_middleware import TitleMiddleware

if TYPE_CHECKING:
    pass


def build_middlewares(
    config: RunnableConfig,
    agent_name: str | None = None,
    custom_middlewares: List[AgentMiddleware] | None = None,
) -> List[AgentMiddleware]:
    """Build middleware chain for agent.

    Args:
        config: RunnableConfig containing app_config in configurable
        agent_name: Optional agent name to load agent-specific middlewares
        custom_middlewares: Optional list of custom middlewares to add

    Returns:
        List of middleware instances
    """

    middlewares: List[AgentMiddleware] = []

    middlewares.append(TitleMiddleware())

    # TODO 根据 agent 定制 middleware

    # Add custom middlewares
    if custom_middlewares:
        middlewares.extend(custom_middlewares)

    return middlewares
