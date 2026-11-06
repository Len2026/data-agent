"""
业务层
"""
import uuid

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.conf.meta_config import MetaConfig, TableConfig, MetricConfig
from app.core.log import logger
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.repositories.es.value_es_repository import ValueEsRepository
from app.repositories.mysql.dw_mysql_repository import DwMySQLRepository
from app.repositories.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class MetaKnowledgeService:
    def __init__(
            self,
            value_es_repo: ValueEsRepository,
            dw_mysql_repo: DwMySQLRepository,
            meta_mysql_repo: MetaMySQLRepository,
            column_qdrant_repo: ColumnQdrantRepository,
            metric_qdrant_repo: MetricQdrantRepository,
            embedding_client: HuggingFaceEndpointEmbeddings
    ):
        self.value_es_repo = value_es_repo
        self.dw_mysql_repo = dw_mysql_repo
        self.meta_mysql_repo = meta_mysql_repo
        self.column_qdrant_repo = column_qdrant_repo
        self.metric_qdrant_repo = metric_qdrant_repo
        self.embedding_client = embedding_client

    async def build(self, config: MetaConfig):
        logger.info('构建业务 开始')
        # 构建业务的核心逻辑。。。。。。。
        # 涉及数据库的操作（调用持久层中的方法）

        # 构建元数据知识库思路：
        # 1.处理表相关的数据
        # 1.1 保存表信息到meta库中的 table_info
        # 1.2 保存字段信息到meta库中的 column_info
        # 1.3 为字段信息建立向量索引
        # 1.4 为字段取值建立全文索引

        # 2.处理指标相关的数据
        # 2.1 保存指标信息到meta库中的 metric_info
        # 2.1 保存指标和字段关联信息到meta库中的 column_metric
        # 2.3 为指标信息建立向量索引

        if config.tables:
            column_infos: list[ColumnInfoMySQL] = await self._save_table_infos_to_meta(config.tables)
            logger.info('保存表信息到meta库')

            await self._save_column_infos_to_meta(column_infos)
            logger.info('保存字段信息到meta库')

            await self._save_column_infos_to_qdrant(column_infos)
            logger.info('为字段信息建立向量索引')

            await self._save_column_values_to_es(column_infos,config.tables)
            logger.info('为字段取值建立全文索引')


        if config.metrics:
            metric_infos: list[MetricInfoMySQL] = await self._save_metric_infos_to_meta(config.metrics)
            logger.info('保存指标信息到meta库')

            await self._save_column_metrics_to_meta(config.metrics)
            logger.info('保存字段和指标的关联信息到meta库')

            await self._save_metric_infos_to_qdrant(metric_infos)
            logger.info('为指标信息建立向量索引')


        logger.info('构建业务 结束')


    async def _save_table_infos_to_meta(self, tables: list[TableConfig])->list[ColumnInfoMySQL]:
        # 收集表信息
        table_infos: list[TableInfoMySQL] = []
        # 收集字段信息
        column_infos: list[ColumnInfoMySQL] = []

        for table in tables:
            # 创建ORM对象
            table_info = TableInfoMySQL(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description
            )
            table_infos.append(table_info)

            # 查询dw库获取当前table中的所有字段的数据类型type -> {字段名：type类型}
            column_types: dict[str, str] = await self.dw_mysql_repo.get_column_types(table.name)

            for column in table.columns:
                # 查询dw库取出指定字段的前8条数据
                column_values: list = await self.dw_mysql_repo.get_column_values(table.name, column.name, 8)
                # 创建ORM对象
                column_info = ColumnInfoMySQL(
                    id=f'{table.name}.{column.name}',
                    name=column.name,
                    type=column_types[column.name],
                    role=column.role,
                    examples=column_values,
                    description=column.description,
                    alias=column.alias,
                    table_id=table.name
                )
                column_infos.append(column_info)

        # 将table_infos存库
        self.meta_mysql_repo.save_table_infos(table_infos)

        # 返回字段信息
        return column_infos



    async def _save_column_infos_to_meta(self, column_infos: list[ColumnInfoMySQL]):
        self.meta_mysql_repo.save_column_infos(column_infos)



    async def _save_column_infos_to_qdrant(self, column_infos: list[ColumnInfoMySQL]):
        # 遍历column_infos列表，对每一个column_info中的name字段、description字段，以及alias中的每一个值进行向量化
        # 每一个point包含 id  vector  payload 部分
        # id 使用uuid生成
        # vector 使用embedding模型向量化
        # payload 当前字段信息的字典

        # 收集每一个point的信息的字典列表
        # [ { id:uuid,text:向量文本,payload:{字段信息的字典} }, {...} ]
        points: list[dict] = []
        for column_info in column_infos:
            payload = ColumnInfoQdrant(
                id=column_info.id,
                name=column_info.name,
                type=column_info.type,
                role=column_info.role,
                examples=column_info.examples,
                alias=column_info.alias,
                description=column_info.description,
                table_id=column_info.table_id
            )

            # name字段
            points.append({
                "id": uuid.uuid4(),
                "text": column_info.name,
                "payload": payload
            })

            # description字段
            points.append({
                "id": uuid.uuid4(),
                "text": column_info.description,
                "payload": payload
            })

            # alias字段
            for alia in column_info.alias:
                points.append({
                    "id": uuid.uuid4(),
                    "text": alia,
                    "payload": payload
                })

        # 获取所有需要向量化的文本
        texts = [point['text'] for point in points]
        # 一次性向量化所有文本，效率低，甚至程序崩溃
        # client.embed_documents(texts)

        # 收集所有的向量
        vectors: list[list[float|int]] = []

        # 每批向量化的数量
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            # i - 0  i - 10  i - 20 ...
            # 截取一批需要向量化的文本
            batch_texts = texts[i:i + batch_size]
            # 向量化一批文本
            batch_vectors = await self.embedding_client.aembed_documents(batch_texts)
            # vectors.append(batch_vectors) # [[[],[],[]]] 多包了一层[]
            vectors.extend(batch_vectors)

        # 获取所有的id
        ids = [point['id'] for point in points]

        # 获取所有的payload
        payloads = [point['payload'] for point in points]

        # 存库
        await self.column_qdrant_repo.upsert_column_vectors(ids, vectors, payloads)



    async def _save_column_values_to_es(self, column_infos: list[ColumnInfoMySQL], tables: list[TableConfig]):
        pass



    async def _save_metric_infos_to_meta(self, metrics: list[MetricConfig])->list[MetricInfoMySQL]:
        pass

    async def _save_column_metrics_to_meta(self, metrics: list[MetricConfig]):
        pass

    async def _save_metric_infos_to_qdrant(self, metric_infos: list[MetricInfoMySQL]):
        pass