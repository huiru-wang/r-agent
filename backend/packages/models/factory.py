import importlib
from typing import Any, Type

from packages.config import ModelConfig


def resolve_class(module_class_str: str) -> Type:
    """Resolve a "module:class" string to a class.

    Args:
        module_class_str: String in format "module.path:ClassName"
                         (e.g., "langchain_openai:ChatOpenAI")

    Returns:
        The resolved class
    """
    if ":" not in module_class_str:
        raise ValueError(
            f"Invalid class string format: '{module_class_str}'. "
            "Expected format: 'module.path:ClassName'"
        )

    module_path, class_name = module_class_str.rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Failed to import module '{module_path}': {e}")

    if not hasattr(module, class_name):
        raise AttributeError(
            f"Module '{module_path}' does not have class '{class_name}'"
        )

    return getattr(module, class_name)


def create_chat_model(model_config: ModelConfig) -> Any:
    """Create a chat model instance from configuration.

    Args:
        model_config: ModelConfig instance with configuration

    Returns:
        Instantiated chat model
    """
    ChatModelClass = resolve_class(model_config.use)

    kwargs = {}

    if model_config.model:
        kwargs["model"] = model_config.model
    if model_config.api_key:
        kwargs["api_key"] = model_config.api_key
    if model_config.base_url:
        kwargs["base_url"] = model_config.base_url

    return ChatModelClass(**kwargs)
