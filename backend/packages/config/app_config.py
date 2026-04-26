import os
import re
from pathlib import Path
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel, Field


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


class ModelConfig(BaseModel):
    """Configuration schema for a chat model."""

    id: str
    display_name: str = ""
    description: str = ""
    use: str
    model: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    supports_vision: bool = False


class ToolConfig(BaseModel):
    """Configuration schema for a tool."""

    name: str
    use: str = ""
    max_results: int = 5


class CheckpointerConfig(BaseModel):
    """Configuration schema for checkpointer."""

    type: str = "sqlite"
    connection_string: str = "checkpoints.db"


class AgentConfig(BaseModel):
    """Configuration schema for an agent."""

    name: str
    model: str = ""
    tools: List[str] = Field(default_factory=list)


class TitleConfig(BaseModel):
    """Title generation configuration."""

    enabled: bool = True
    model: Optional[str] = None


class SummarizationConfig(BaseModel):
    """Summarization configuration."""

    enabled: bool = True
    model: Optional[str] = None
    max_tokens: int = 500


class MemoryConfig(BaseModel):
    """Memory configuration."""

    enabled: bool = True
    storage_path: str = "memory.json"
    debounce_seconds: int = 30
    model_name: Optional[str] = None
    max_facts: int = 100
    fact_confidence_threshold: float = 0.7
    injection_enabled: bool = True
    max_injection_tokens: int = 2000


class SkillEvolutionConfig(BaseModel):
    """Skill evolution configuration."""

    enabled: bool = False
    evaluation_interval: int = 100
    improvement_threshold: float = 0.1


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

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AppConfig":
        """Load configuration from a YAML file.

        Args:
            path: Path to config.yaml file

        Returns:
            AppConfig instance with resolved environment variables
        """
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

    def get_model_config(self, id: str) -> Optional[ModelConfig]:
        """Get model configuration by name."""
        for model in self.models:
            if model.id == id:
                return model
        return None

    def get_tool_config(self, name: str) -> Optional[ToolConfig]:
        """Get tool configuration by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_agent_config(self, name: str) -> Optional[AgentConfig]:
        """Get agent configuration by name."""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
