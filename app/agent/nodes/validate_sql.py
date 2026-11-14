from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState


# 节点：校验SQL
def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage": "校验SQL"})

    # return {"error": None} # 校验成功
    return {"error": "error message"} # 校验失败