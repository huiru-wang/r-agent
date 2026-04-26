import os
import re
from pathlib import Path
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel, Field
from .schema import (
    AgentConfig,
    CheckpointerConfig,
    MemoryConfig,
    ModelConfig,
    SkillEvolutionConfig,
    SummarizationConfig,
    TitleConfig,
    ToolConfig,
)


def resolve_env_vars(value: Any) -> Any:
    """Recursively resolve environment variables in strings.

    Replaces $VAR and ${VAR} patterns with os.environ.get("VAR").
    """
    if isinstance(value, str):
        pattern = r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?"
        return re.sub(pattern, lambda m: os.environ.get(m.group(1), m.group(0)), value)
    elif isinstance(value, dict):
        return {k: resolve_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_env_vars(item) for item in value]
    return value


class AppConfig(BaseModel):
    """Application configuration loaded from config.yaml.

    This is the unified entry point for all configuration.
    """

    log_level: str = "info"
    token_usage_enabled: bool = False
    models: List[ModelConfig] = Field(default_factory=list)
    tools: List[ToolConfig] = Field(default_factory=list)
    agents: List[AgentConfig] = Field(default_factory=list)
    checkpointer: Optional[CheckpointerConfig] = None
    title: Optional[TitleConfig] = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AppConfig":
        """从配置文件加载配置"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r") as f:
            raw_config = yaml.safe_load(f)

        config_data = resolve_env_vars(raw_config)

        # Flatten token_usage into token_usage_enabled
        if "token_usage" in config_data:
            config_data["token_usage_enabled"] = config_data["token_usage"].get(
                "enabled", False
            )

        # Parse nested configs
        if "title" in config_data and config_data["title"]:
            config_data["title"] = TitleConfig(**config_data["title"])

        if "summarization" in config_data and config_data["summarization"]:
            config_data["summarization"] = SummarizationConfig(
                **config_data["summarization"]
            )

        if "memory" in config_data and config_data["memory"]:
            config_data["memory"] = MemoryConfig(**config_data["memory"])

        if "skill_evolution" in config_data and config_data["skill_evolution"]:
            config_data["skill_evolution"] = SkillEvolutionConfig(
                **config_data["skill_evolution"]
            )

        if "checkpointer" in config_data and config_data["checkpointer"]:
            config_data["checkpointer"] = CheckpointerConfig(
                **config_data["checkpointer"]
            )

        return cls.model_validate(config_data)


# Global app config instance
_app_config: Optional[AppConfig] = None


def load_app_config(path: str | Path) -> "AppConfig":
    """Load and set the global app config from a YAML file."""
    global _app_config
    _app_config = AppConfig.from_yaml(path)
    return _app_config


def get_app_config() -> "AppConfig":
    """Get the global app config, loading from default path if needed."""
    global _app_config
    if _app_config is None:
        default_path = Path(__file__).parent.parent.parent / "config.yaml"
        _app_config = AppConfig.from_yaml(default_path)
    return _app_config


def get_model_config(id: str | None = None) -> "ModelConfig | None":
    """Get model config by id, or first model if id is None."""
    app_config = get_app_config()
    if id is None:
        return app_config.models[0] if app_config.models else None
    for model in app_config.models:
        if model.id == id:
            return model
    return None


def get_tool_config(name: str) -> "ToolConfig | None":
    """Get tool config by name."""
    app_config = get_app_config()
    for tool in app_config.tools:
        if tool.name == name:
            return tool
    return None


def get_agent_config(name: str) -> "AgentConfig | None":
    """Get agent config by name."""
    app_config = get_app_config()
    for agent in app_config.agents:
        if agent.name == name:
            return agent
    return None


def get_title_config() -> "TitleConfig":
    """Get title generation config from app config."""
    title_config = get_app_config().title
    if title_config is None:
        return TitleConfig()
    return title_config
