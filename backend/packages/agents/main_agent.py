from pathlib import Path
from typing import Any, Dict

from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from packages.config.app_config import AppConfig
from packages.middleware.facotry import build_middlewares
from packages.models.factory import create_chat_model
from packages.tools.tools import get_available_tools

from packages.agents.prompt import SYSTEM_PROMPT_TEMPLATE

# Global config instance for LangGraph Local Server
_config_cache: AppConfig | None = None


def _get_app_config() -> AppConfig:
    """Get or load AppConfig singleton."""
    global _config_cache
    if _config_cache is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        _config_cache = AppConfig.from_yaml(config_path)
    return _config_cache


def create_main_agent(config: RunnableConfig | None = None) -> Any:
    """Create the main agent with tools and middleware.

    Args:
        config: Optional RunnableConfig. If not provided, loads from default config.yaml.
                When called by LangGraph Local Server, config may be None or empty.

    Returns:
        Configured agent Runnable
    """
    # Load app_config - either from config or from default yaml
    if config is None:
        app_config = _get_app_config()
        agent_name = "main_agent"
        model_id = None
    else:
        cfg = config.get("configurable", {})
        app_config = cfg.get("app_config")
        if app_config is None:
            app_config = _get_app_config()
        agent_name = cfg.get("agent_name", "main_agent")
        model_id = cfg.get("model_id") or cfg.get("model")

    agent_config = app_config.get_agent_config(agent_name)

    # Fallback: get model_id from agent_config if not provided directly
    if not model_id and agent_config and agent_config.model:
        model_id = agent_config.model

    # Default to first model if still not found
    if not model_id and app_config.models:
        model_id = app_config.models[0].id

    if not model_id:
        raise ValueError(
            "model_id must be provided in config or agent_config or default to first model"
        )

    model_config = app_config.get_model_config(model_id)
    if not model_config:
        raise ValueError(f"Model config not found for: {model_id}")

    # Build system prompt from template
    prompt_data: Dict[str, str] = {
        "agent_name": agent_name,
        "soul": "You are helpful, harmless, and honest.",
        "memory_context": "",
        "subagent_thinking": "",
        "skills_section": "",
        "deferred_tools_section": "",
        "subagent_section": "",
        "subagent_reminder": "",
    }
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(**prompt_data)

    # Prepare config for tools/middleware lookup
    runnable_config = config or {}
    configurable = runnable_config.get("configurable", {}) if runnable_config else {}
    if "app_config" not in configurable:
        configurable["app_config"] = app_config
    runnable_config["configurable"] = configurable

    # Get tools and middleware
    tools = get_available_tools(config=runnable_config, agent_config=agent_config)
    middlewares = build_middlewares(config=runnable_config, agent_name=agent_name)

    # Create chat model
    model = create_chat_model(model_config)

    # Create agent
    agent = create_agent(
        model=model, tools=tools, system_prompt=system_prompt, middleware=middlewares
    )

    return agent
