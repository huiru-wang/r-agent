"""Task executor - LLM streaming call implementation."""

import asyncio
from typing import Any

from packages.agents.main_agent import create_main_agent
from packages.runtime.run.manager import RunManager
from packages.runtime.run.schema import RunRecord, RunStatus


async def run_task(
    manager: RunManager,
    record: RunRecord,
) -> Any:
    """LLM Worker - Core async function for task execution.

    Args:
        manager: RunManager instance for tracking task state
        record: RunRecord containing task information and configuration

    Returns:
        The result of the agent execution
    """
    task_id = record.task_id
    print(f"[run_task] {task_id}-{record.name} 开始执行")

    record.status = RunStatus.RUNNING

    try:
        # Create agent from configuration
        agent = create_main_agent(config=record.config)

        # Execute agent with input messages
        result = await agent.ainvoke(
            {"messages": record.input_messages},
            config=record.config,
        )

        record.result = result
        record.status = RunStatus.SUCCESS
        print(f"[run_task] {task_id}-{record.name} 执行成功")
        return result

    except asyncio.CancelledError:
        record.status = RunStatus.CANCELLED
        print(f"[run_task] {task_id}-{record.name} 取消异常")
        raise

    except Exception as e:
        record.error = str(e)
        record.status = RunStatus.FAILED
        print(f"[run_task] {task_id}-{record.name} 执行失败: {e}")
        raise
