from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class ColumnQdrantRepository:
    collection_name = 'columns_collection'
    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def upsert_column_vectors(self, ids: list[str], vectors: list[list[float]], payloads: list[ColumnInfoQdrant]):
        # 判断集合存在则删除
        if await self.client.collection_exists(collection_name=self.collection_name):
            await self.client.delete_collection(collection_name=self.collection_name)

        # 创建集合
        await self.client.create_collection(
            collection_name=self.collection_name,  # 集合名称
            vectors_config=models.VectorParams(  # 向量的配置信息
                size=app_config.qdrant.embedding_size,  # 向量维度(取决于enbedding模型)
                distance=models.Distance.COSINE  # 向量相似度的算法
            )
        )

        # 添加数据(一次性添加所有数据)
        # await self.client.upsert(
        #     collection_name=self.collection_name,
        #     points=[
        #         models.PointStruct(
        #             id=ids[i],
        #             payload=payloads[i],
        #             vector=vectors[i]
        #         )
        #         for i in range(len(ids))
        #     ],
        # )

        # 分批添加数据
        batch_size = 10
        for i in range(0, len(ids), batch_size):
            # 获取分批数据
            batch_ids = ids[i:i + batch_size]
            batch_vectors = vectors[i:i + batch_size]
            batch_payloads = payloads[i:i + batch_size]
            await self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=batch_ids[n],
                        payload=batch_payloads[n],
                        vector=batch_vectors[n]
                    )
                    for n in range(len(batch_ids))
                ]
            )
