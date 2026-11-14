"""
状态图（图构建器）：StateGraph实例
节点：实现特定功能的函数
状态：包含多个可变数据的对象，在图的各个节点上流传
边：两个节点的连线，表示节点的执行顺序

节点函数的参数：
state: 状态对象（保存可变的数据）
runtime：运行时对象
    stream_writer：向调用者输出自定数据的方法
    context：图的上下文信息（保存固定的数据/依赖模块）
config：配置对象（不常用）
"""
import asyncio
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


# state数据模型
class MyState(TypedDict):
    query: str
    keywords: list[str]
    sql: str

# context数据模型
class MyContext(TypedDict):
    dw_mysql_repo: str
    meta_mysql_repo: str

# 节点：提取关键字
def extract_keyword(state: MyState, runtime: Runtime[MyContext], config: RunnableConfig):
    print('执行extract_keyword节点')

    # 向图外部输出数据
    runtime.stream_writer('提取关键字')

    # 获取上下文信息
    print(f'context信息: {runtime.context["dw_mysql_repo"]}')
    
    # 提取的关键字
    keywords = ['你好','推翻','儿童']

    # 更新状态数据
    # state['keywords'] = keywords # 不推荐

    return {"keywords": keywords} # 推荐


# 节点：生成SQL
def generate_sql(state: MyState, runtime: Runtime[MyContext], config: RunnableConfig):
    print('执行generate_sql节点')

    # 向图外部输出数据
    runtime.stream_writer('生成SQL')

    # 获取上下文信息
    print(f'context信息: {runtime.context["meta_mysql_repo"]}')

    # 生成SQL
    sql = 'select * from customer'

    # 更新状态数据
    return {"sql": sql}  # 推荐


# 创建图构建器
graph_builder = StateGraph(
    state_schema=MyState,
    context_schema=MyContext
)

# 添加节点
graph_builder.add_node('extract_keyword',extract_keyword)
graph_builder.add_node('generate_sql',generate_sql)

# 添加边
graph_builder.add_edge(START,"extract_keyword")
graph_builder.add_edge("extract_keyword","generate_sql")
graph_builder.add_edge("generate_sql",END)

# 编译图
graph = graph_builder.compile()


if __name__ == '__main__':
    async def test():
        # 创建state对象
        state = MyState(query='你好啊')

        # 创建context对象
        context = MyContext(dw_mysql_repo='111',meta_mysql_repo='222')

        # 异步流式执行图
        async for chunk in graph.astream(
            input=state,
            context=context,
            # updates 获得增量数据（节点里return的数据）
            # values 更新合并后的state数据
            # custom 获得runtime.stream_writer输出的数据
            stream_mode='custom'
        ):
            print('---------------------',chunk)


    asyncio.run(test())