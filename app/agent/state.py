from typing import TypedDict

from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class DataAgentState(TypedDict):
    query: str
    keywords: list[str]
    recall_columns: list[ColumnInfoQdrant]
    error: str | None

