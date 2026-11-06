import asyncio

from sqlalchemy import text, Select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from app.conf.app_config import DBConfig, app_config
from app.models.mysql.table_info_mysql import TableInfoMySQL

class MySQLClientManager:
    # 创建实例属性
    def __init__(self, config: DBConfig):
        self.config = config
        self.engine: AsyncEngine | None = None  # 引擎类型
        self.session_factory: async_sessionmaker | None = None

    # 获取连接url
    def _get_url(self):
        # "mysql+asyncmy://user:pass@hostname/dbname?charset=utf8mb4"
        # 协议    mysql驱动 用户名 密码 主机名      数据库名
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}/{self.config.database}?charset=utf8mb4"

    # 初始化
    def init(self):
        # 创建异步引擎
        self.engine = create_async_engine(
            self._get_url(),
            pool_size=10,  # 连接池的初始创建常驻连接数，用完之后归还连接池    优化(1)
            pool_pre_ping=True  # 每次从连接池中获取连接时，会执行一个ping操作（检测是否能正常使用）   优化(1)
        )

        # 创建异步会话的工厂函数   优化(3)
        self.session_factory = async_sessionmaker(
            self.engine,
            autoflush=True,  # 自动刷新，未提交事务的 变动/修改 也能查询到最新的数据
            autobegin=True,  # 自动开启事务
            expire_on_commit=False  # 提交事务之后，ORM对象是否过期
        )

    # 关闭引擎，释放资源
    async def close(self):
        await self.engine.dispose()

# 创建客户端管理器
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)
meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)

if __name__ == '__main__':
    async def test():
        # 初始化客户端
        dw_mysql_client_manager.init()

        # 创建异步会话（通过会话对象操作数据库）
        # async with AsyncSession(
        #         dw_mysql_client_manager.engine,
        #         autoflush=True, # 自动刷新，未提交事务的 变动/修改 也能查询到最新的数据    优化(2)
        #         autobegin=True, # 自动开启事务                              优化(2)
        #         expire_on_commit=False # 提交事务之后，ORM对象是否过期     优化(2)
        # ) as session:

        # 使用会话工厂创建session
        async with dw_mysql_client_manager.session_factory() as session:    # 优化(3)
            # session.begin() # 开启事务

            # 添加数据
            # 。。。。。。

            # 查询数据
            # text('select * from dim_customer limit 3') 将sql字符串转成可执行对象
            result = await session.execute(text('select * from dim_customer limit 3'))
            # print(result) # CursorResult object

            # print(result.all()) # [('C001', '李伟', '男', '黄金'), ('C002', '王芳', '女', '白银'), ('C003', '张敏', '女', '黄金')]

            # print(result.mappings().all()) # [{...},{...},{...}]

            # print(result.scalars().all()) # ['C001','C002','C003']

            print(result.scalar())  # 'C001'

        # 关闭客户端
        await dw_mysql_client_manager.close()

    # 执行协程
    # asyncio.run(test())

    async def test2():
        # 初始化客户端
        meta_mysql_client_manager.init()

        # 使用会话工厂创建session
        async with meta_mysql_client_manager.session_factory() as session:
            # 创建ORM对象

            table_info1 = TableInfoMySQL(
                id='11',
                name='test11',
                role='dim',
                description='测试ORM操作11'
            )
            table_info2 = TableInfoMySQL(
                id='22',
                name='test22',
                role='dim',
                description='测试ORM操作22'
            )

            # 添加单条数据
            # session.add(table_info1)
            # session.add(table_info2)

            # 添加多条数据
            # session.add_all([table_info1, table_info2])

            # 查询一条数据
            # result = await session.get(TableInfoMySQL,'22')
            # print(result) # ORM对象
            # print(result.name) # test22

            # 提交事务
            # await session.commit()

            # 查询多条数据
            # results = await session.execute(
            #     Select(TableInfoMySQL).limit(2)
            # )
            # print(results.scalars().all()) # [ORM对象,ORM对象]

            # 修改数据
            table1 = await session.get(TableInfoMySQL, '11')
            table1.name = 'test33'

            # 删除数据
            # await session.delete(table_info1) # 不能删除，table_info1是一个新对象，与数据库中的数据没有映射关系
            # await session.delete(table1) # 可以删除

            # 提交事务
            await session.commit()

        # 关闭客户端
        await meta_mysql_client_manager.close()

    # 执行协程
    asyncio.run(test2())

