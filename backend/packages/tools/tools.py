import importlib
from typing import TYPE_CHECKING, Any, List

from langchain_core.runnables import RunnableConfig

if TYPE_CHECKING:
    from packages.config.app_config import AgentConfig

# Tool registry: maps tool names to "module:class" strings
TOOL_REGISTRY = {
    "web_search": "packages.tools.builtins.web_search:web_search",
}


def get_available_tools(
    config: RunnableConfig,
    agent_config: "AgentConfig | None" = None,
) -> List[Any]:
    """Get available tools based on configuration.

    Args:
        config: RunnableConfig containing app_config in configurable
        agent_config: Optional AgentConfig specifying which tools to load

    Returns:
        List of instantiated tool objects
    """
    cfg = config.get("configurable", {})
    app_config = cfg.get("app_config")

    if not app_config:
        return []

    tools = []
    tool_names = agent_config.tools if agent_config else []

    for name in tool_names:
        # Resolve tool from registry
        if name not in TOOL_REGISTRY:
            continue

        module_class_str = TOOL_REGISTRY[name]
        module_path, class_name = module_class_str.rsplit(":", 1)

        try:
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)

            # If it's already a tool instance (from @tool decorator), use it directly
            # Otherwise instantiate it as a class
            from langchain_core.tools import BaseTool
            if isinstance(tool_class, BaseTool):
                tool_instance = tool_class
            else:
                tool_instance = tool_class()

            tools.append(tool_instance)

        except (ImportError, AttributeError) as e:
            print(f"Failed to load tool '{name}': {e}")
            continue

    return tools
