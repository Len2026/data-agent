"""
HuggingFaceEndpointEmbeddings(url)

.embed_query()  # 对指定文本进行向量化

.embed_documents([text1, text2])    # 一次性批量向量化

"""
import asyncio
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings
from app.conf.app_config import EmbeddingConfig, app_config
class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: HuggingFaceEndpointEmbeddings | None = None

    def _get_url(self):
        return f'http://{self.config.host}:{self.config.port}'

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())

    # Embedding客户端不需要关闭（自动关闭）

# 创建embedding客户的管理器
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    async def test():
        # 初始化客户端
        embedding_client_manager.init()
        # 获取客户端
        client = embedding_client_manager.client

        # 对指定文本进行向量化
        text1 = 'hello'
        text2 = 'world'

        # vector = client.embed_query(text1)
        # print(len(vector)) # 1024

        vectors = client.embed_documents([text1, text2])
        print(vectors) # [[...],[...]]

    asyncio.run(test())