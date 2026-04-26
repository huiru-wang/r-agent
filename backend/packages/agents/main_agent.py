from typing import Any, Dict

from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from packages.config.app_config import (
    get_app_config,
    get_model_config,
    get_agent_config,
)
from packages.middleware.facotry import build_middlewares
from packages.models.factory import create_chat_model
from packages.tools.tools import get_available_tools

from packages.agents.prompt import SYSTEM_PROMPT_TEMPLATE


def create_main_agent(config: RunnableConfig | None = None) -> Any:
    """Create the main agent with tools and middleware.

    Args:
        config: Optional RunnableConfig. If not provided, loads from default config.yaml.
                When called by LangGraph Local Server, config may be None or empty.

    Returns:
        Configured agent Runnable
    """
    # 获取 app config 默认配置
    if config is None:
        app_config = get_app_config()
        agent_name = "main_agent"
        model_id = None
    else:
        cfg = config.get("configurable", {}) or {}
        app_config = cfg.get("app_config")
        if (
            app_config is None
            or not hasattr(app_config, "models")
            or not app_config.models
        ):
            app_config = get_app_config()
        agent_name = cfg.get("agent_name", "main_agent")
        model_id = cfg.get("model_id") or cfg.get("model") or None
        # Normalize empty string to None
        if model_id is not None and not str(model_id).strip():
            model_id = None

    # agent 配置
    agent_config = get_agent_config(agent_name)

    # 未指定model，获取agent配置的 model
    if not model_id and agent_config and agent_config.model:
        model_id = agent_config.model

    # agent未配置model，获取app配置的首个model
    if not model_id and app_config.models:
        model_id = app_config.models[0].id

    if not model_id:
        raise ValueError(
            "model_id must be provided in config or agent_config or default to first model"
        )

    model_config = get_model_config(model_id)
    if not model_config:
        raise ValueError(f"Model config not found for: {model_id}")

    # 构建 system prompt
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

    # tools
    tools = get_available_tools(config=runnable_config, agent_config=agent_config)

    # middleware
    middlewares = build_middlewares(config=runnable_config, agent_name=agent_name)

    model = create_chat_model(model_id)

    # 创建 agent
    agent = create_agent(
        model=model, tools=tools, system_prompt=system_prompt, middleware=middlewares
    )

    return agent
