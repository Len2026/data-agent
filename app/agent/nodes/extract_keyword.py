import jieba.analyse
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


# 节点：提取关键字
def extract_keyword(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 输出给前端的数据
    runtime.stream_writer({"stage": "提取关键字"})

    query = state["query"]

    # 定义返回指定词性的元组
    allow_pos = (
        "n",  # 名词: 数据、服务器、表格
        "nr",  # 人名: 张三、李四
        "ns",  # 地名: 北京、上海
        "nt",  # 机构团体名: 政府、学校、某公司
        "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
        "v",  # 动词: 运行、开发
        "vn",  # 名动词: 工作、研究
        "a",  # 形容词: 美丽、快速
        "an",  # 名形词: 难度、合法性、复杂度
        "eng",  # 英文
        "i",  # 成语
        "l",  # 常用固定短语
        "d",  # 副词
        "m",  # 数词
        "q",  # 量词
        "mq",  # 数量词
        "t",  # 时间
        "TIME"  # 时间
    )

    results: list[str] = jieba.analyse.extract_tags(query, allowPOS=allow_pos)
    # query = '统计3月份各个地区的销售总额'
    # print(results) # ['销售总额', '统计', '月份', '地区']

    # 确保不丢失问题的原语义，关键词列表+query（兜底）
    keywords: list[str] = list(set(results + [query]))

    logger.info(f'提取关键词：{keywords}')

    # 更新状态
    return {"keywords": keywords}
