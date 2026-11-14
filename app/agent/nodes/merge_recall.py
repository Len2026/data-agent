from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


# 节点：合并召回信息
def merge_recall(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage": "合并召回信息"})

    return {}