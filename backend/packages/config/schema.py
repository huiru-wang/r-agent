from pydantic import BaseModel, Field
from typing import List, Optional


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
    model_name: Optional[str] = None
    max_chars: int = 60
    max_words: int = 6


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
