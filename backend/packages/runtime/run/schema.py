import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional

from langchain_core.runnables import RunnableConfig


class RunStatus(Enum):
    """Task status enum."""

    PENDING = "pending"  # Waiting to execute
    RUNNING = "running"  # Currently executing
    SUCCESS = "success"  # Completed successfully
    FAILED = "failed"  # Execution failed
    CANCELLED = "cancelled"  # Cancelled by user


@dataclass
class RunRecord:
    """Stores task information and state."""

    task_id: str
    name: str
    status: RunStatus = RunStatus.PENDING
    result: Any = None
    error: str | None = None
    config: Optional[RunnableConfig] = None
    input_messages: List[Any] = field(default_factory=list)
    _task: asyncio.Task | None = field(default=None, repr=False)
    _cancel_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)
