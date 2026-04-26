"""任务管理器"""

import uuid
from typing import TYPE_CHECKING

from backend.packages.runtime.run.schema import RunStatus
from backend.packages.runtime.run.schema import RunRecord

if TYPE_CHECKING:
    pass


class RunManager:
    """管理所有任务记录"""

    def __init__(self):
        self._tasks: dict[str, RunRecord] = {}

    def create(self, name: str) -> RunRecord:
        """创建一个新任务记录"""
        task_id = str(uuid.uuid4())[:8]
        record = RunRecord(task_id=task_id, name=name)
        self._tasks[task_id] = record
        print(f"[TaskManager] 创建任务: {task_id} ({name})")
        return record

    def get(self, task_id: str) -> RunRecord | None:
        """获取任务记录"""
        return self._tasks.get(task_id)

    def list_all(self) -> list[RunRecord]:
        """列出所有任务"""
        return list(self._tasks.values())

    def is_running(self, task_id: str) -> bool:
        """检查任务是否正在运行"""
        record = self._tasks.get(task_id)
        return record is not None and record.status == RunStatus.RUNNING

    def cancel(self, task_id: str):
        """取消指定任务"""
        record = self._tasks.get(task_id)
        if record:
            record._cancel_event.set()

    def is_cancelled(self, task_id: str) -> bool:
        """检查任务是否已被取消"""
        record = self._tasks.get(task_id)
        return record is not None and record._cancel_event.is_set()
