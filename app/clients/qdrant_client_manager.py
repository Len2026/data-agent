"""

AsyncQdrantClient(url)  # 创建qdrant客户端

.collection_exists()    # 判断集合存在则删除

.create_collection()    # 创建集合

.upsert()   # 添加数据 / 修改数据
        collection_name="test_collection",
                points=[
                    models.PointStruct(
                        id=11,
                        payload={
                            "color": "red",
                            "num": 1
                        },
                        vector=[0.9, 0.1, 0.1, 0.5]
                    ),

.query_points() # 查询
         response = await client.query_points(
            collection_name="test_collection",
            query=[0.9, 0.1, 0.2, 0.5],
            limit=2, # 返回相似度最高的前2条数据
            score_threshold=0.6, # 阈值，返回大于等阈值的数据
            query_filter=models.Filter(
                must=[models.FieldCondition(
                    key="num", # 根据payload中的键过滤数据
                    match=models.MatchValue(value=2) # 根据指定的键的值过滤数据
                )]
            )
        )
client.delete() # 删除
            collection_name="test_collection",
            points_selector=[11,33] # 删除id为11和33的点

"""
import asyncio

from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client: AsyncQdrantClient | None = None

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = AsyncQdrantClient(self._get_url())

    async def close(self):
        await self.client.close()

# 创建qdrant客户端管理器
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

# if __name__ == '__main__':
#     async def test():
#         # 初始化客户端
#         qdrant_client_manager.init()
#         # 获取客户端
#         client = qdrant_client_manager.client
#
#         # 判断集合存在则删除   .collection_exists()
#         if await client.collection_exists(collection_name="test_collection"):
#             await client.delete_collection(collection_name="test_collection")
#
#         # 创建集合    .create_collection()
#         await client.create_collection(
#             collection_name="test_collection", # 集合名称
#             vectors_config=models.VectorParams( # 向量的配置信息
#                 size=4, # 向量维度(取决于embedding模型)
#                 distance=models.Distance.COSINE # 向量相似度的算法
#             )
#         )
#
#         # 添加数据 / 修改数据
#         await client.upsert(
#             collection_name="test_collection",
#             points=[
#                 models.PointStruct(
#                     id=11,
#                     payload={
#                         "color": "red",
#                         "num": 1
#                     },
#                     vector=[0.9, 0.1, 0.1, 0.5]
#                 ),
#                 models.PointStruct(
#                     id=22,
#                     payload={
#                         "color": "blue",
#                         "num": 2
#                     },
#                     vector=[0.9, 0.4, 0.1, 0.5]
#                 ),
#                 models.PointStruct(
#                     id=33,
#                     payload={
#                         "color": "yellow",
#                         "num": 1
#                     },
#                     vector=[0.9, 0.1, 0.5, 0.5]
#                 ),
#                 models.PointStruct(
#                     id=44,
#                     payload={
#                         "color": "pink",
#                         "num": 1
#                     },
#                     vector=[0.9, -0.1, 0.1, 0.5]
#                 ),
#                 models.PointStruct(
#                     id=55,
#                     payload={
#                         "color": "orange",
#                         "num": 2
#                     },
#                     vector=[0.1, 0.1, 0.1, 0.5]
#                 ),
#                 models.PointStruct(
#                     id=66,
#                     payload={
#                         "color": "red",
#                         "num": 1
#                     },
#                     vector=[0.9, 0.1, 0.8, 0.5]
#                 )
#             ],
#         )
#
#         # 查询数据
#         response = await client.query_points(
#             collection_name="test_collection",
#             query=[0.9, 0.1, 0.2, 0.5],
#             limit=2, # 返回相似度最高的前2条数据
#             score_threshold=0.6, # 阈值，返回大于等阈值的数据
#             query_filter=models.Filter(
#                 must=[models.FieldCondition(
#                     key="num", # 根据payload中的键过滤数据
#                     match=models.MatchValue(value=2) # 根据指定的键的值过滤数据
#                 )]
#             )
#         )
#         print(response.points) # [ScoredPoint,ScoredPoint]
#         print(response.points[1].payload['color']) # pink
#
#
#         # 删除数据
#         # await client.delete(
#         #     collection_name="test_collection",
#         #     points_selector=[11,33] # 删除id为11和33的点
#         # )
#
#         # 关闭客户端
#         await qdrant_client_manager.close()
#
#     asyncio.run(test())