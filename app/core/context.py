# ContextVar 上下文变量
# ContextVar 作用是在多个异步任务之间隔离数据（多个协程中的上下文变量不会相互覆盖）
import asyncio
from _contextvars import ContextVar

# request_id 上下文变量名称
# default='None' 指定默认值，上下文变量没有值时，返回默认值
_request_id_context_var: ContextVar = ContextVar("request_id",default='None')

# 获取上下文变量的值
def get_req_id()->str:
    return _request_id_context_var.get()

# 设置上下文变量的值
def set_req_id(rid: str):
    _request_id_context_var.set(rid)


if __name__ == '__main__':
    # 模拟两个异步请求
    async def request1():
        print(f'请求1开始执行，request_id={get_req_id()}') # None
        set_req_id('111')
        print(f'请求1结束执行，request_id={get_req_id()}') # 111

    async def request2():
        print(f'请求2开始执行，request_id={get_req_id()}') # None
        set_req_id('222')
        print(f'请求2结束执行，request_id={get_req_id()}') # 222

    async def main():
        await asyncio.gather(request1(), request2())

    asyncio.run(main())