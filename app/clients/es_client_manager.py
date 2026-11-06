"""
AsyncElasticsearch()

.indices.create()   # 创建索引

.index()  # 添加单个文档

.bulk() # 添加多个文档

 print(results['hits']['hits'][0]['_source'])
"""
import asyncio
from elasticsearch import AsyncElasticsearch
from app.conf.app_config import ESConfig, app_config

class EsClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: AsyncElasticsearch | None = None

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = AsyncElasticsearch(self._get_url())

    async def close(self):
        await self.client.close()

# 创建ES客户端管理器
es_client_manager = EsClientManager(app_config.es)

if __name__ == '__main__':
    async def test():
        es_client_manager.init()
        client = es_client_manager.client

        # 如果存在则删除索引
        if await client.indices.exists(index='test-index'):
            await client.indices.delete(index='test-index')

        # 创建索引
        await client.indices.create(
            index="test-index",
            mappings={
                "dynamic": False, # 关闭动态映射
                "properties": { # 文档的属性
                    "name": { # 字段
                        "type": "text" # 用于全文检索
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            },
        )

        # 添加单个文档
        await client.index(
            index="test-index",
            document={
                "name": "Snow Crash",
                "author": "Neal Stephenson",
                "release_date": "1992-06-01",
                "page_count": 470
            },
        )

        # 添加多个文档
        await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": "test-index"
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": "test-index"
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": "test-index"
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": "test-index"
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": "test-index"
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
            # refresh=True # 刷新数据，每添加一个文档刷新一次（太频繁了）
        )


        # ES默认1秒后刷新索引
        await asyncio.sleep(1)


        # 查询数据
        results = await client.search(
            index="test-index",
            query={ # 查询条件
                "match": { # 设置查询的键和值
                    "name": "brave"
                }
            },
        )
        # {'name': 'Snow Crash', 'author': 'Neal Stephenson', 'release_date': '1992-06-01', 'page_count': 470}
        print(results['hits']['hits'][0]['_source'])

        await es_client_manager.close()

    asyncio.run(test())
    
