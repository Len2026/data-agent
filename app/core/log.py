"""
日志管理的目标：

1.定制日志输出格式，控制输出级别

2.自动将日志保存到日志文件

3.设置日志文件的大小，超过会自动创建一个新的文件

4.指定日志文件的有效期，过期会自动删除文件

5.记录当前日志输出是哪个请求的ID
"""
import sys
import uuid
from pathlib import Path

from loguru import logger

from app.conf.app_config import app_config
from app.core.context import get_req_id

# 移除默认输出格式
logger.remove()

# 配置日志格式
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "  # 绿色显示日志时间（精确到毫秒）
    "<level>{level: <8}</level> | "  # 按级别颜色显示日志级别（左对齐，占8个字符）
    "<magenta>request_id - {extra[request_id]}</magenta> | "  # 品红色显示request_id（从日志extra中获取）
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "  # 青色显示日志所在文件、函数、行号
    "<level>{message}</level>"  # 按级别颜色显示日志正文
)

# 注入请求id的函数（不需要我们调用）
def inject_request_id(record):
    """
    Loguru 日志补丁函数：为日志记录对象注入 request_id（请求唯一标识）
    保证每条日志都能关联到对应的请求，便于问题排查和请求链路追踪

    Args:
        record: Loguru 的日志记录对象，包含日志的所有上下文信息（如时间、级别、extra 等）
    """

    # 获取请求id
    request_id = get_req_id()

    if request_id == "None":
        # 使用uuid生成请求id
        request_id = uuid.uuid4()

    # 将 request_id 存入日志记录的 extra 字段，供日志格式中 {extra[request_id]} 调用
    record["extra"]["request_id"] = request_id


# 给日志打补丁，使其在输出每一条日志前执行 inject_request_id 函数，注入request_id
logger = logger.patch(inject_request_id)


# 如果配置中开启控制台日志输出
if app_config.logging.console.enable:
    # 添加控制台日志输出
    logger.add(
        sink=sys.stdout, # 日志位置：控制台
        level=app_config.logging.console.level, # 日志级别
        format=log_format # 日志格式
    )

# 如果配置中开启文件日志输出
if app_config.logging.file.enable:
    # 获取日志文件路径
    log_path = Path(__file__).parents[2] / "logs/app.log"

    # 添加文件日志输出
    logger.add(
        sink=log_path, # 日志位置：文件
        level=app_config.logging.file.level, # 日志级别
        format=log_format, # 日志格式
        rotation=app_config.logging.file.rotation, # 日志文件按大小轮换(创建新的日志文件)
        retention=app_config.logging.file.retention, # 日志的有效期
        encoding="utf-8" # 日志文件的编码
    )


if __name__ == '__main__':
    # loguru有默认的输出格式：2026-11-04 08:46:40.891 | INFO     | __main__:<module>:18 - 普通信息
    logger.debug('调试信息')
    logger.info('普通信息')
    logger.warning('警告信息')
    logger.error('错误信息')
    logger.critical('严重错误')

    # 需要定制日志输出格式，先移除默认输出格式
