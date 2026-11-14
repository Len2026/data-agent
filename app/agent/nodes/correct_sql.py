from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


# 节点：校正SQL
def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage": "校正SQL"})

    return {}