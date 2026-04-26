from langchain.agents.middleware import AgentMiddleware
from langchain.agents import AgentState
from typing import NotRequired, override


class TitleMiddlewareState(AgentState):
    """Compatible with the `ThreadState` schema."""

    title: NotRequired[str | None]


class TitleMiddleware(AgentMiddleware):
    """第一次对话后自动生成标题"""

    state_schema = TitleMiddlewareState

    def _should_generate_title(self, state):
        messages = state.get("messages", [])

        # 条件：没有标题 + 至少有1个用户消息和1个助手消息
        if state.get("title"):
            return False
        if len(messages) < 2:
            return False

        user_count = sum(1 for m in messages if m.type == "human")
        return user_count == 1  # 第一次对话

    def _generate_title(self, state):
        """生成标题"""

        # 取用户消息作为 fallback 标题
        user_msg = state["messages"][0].content

        if not isinstance(user_msg, str):
            return None

        # TODO
        return user_msg[:50] + ("..." if len(user_msg) > 50 else "")

    @override
    def after_model(self, state, runtime):
        if not self._should_generate_title(state):
            return None

        return {"title": self._generate_title(state)}
