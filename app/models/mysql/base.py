from sqlalchemy.orm import DeclarativeBase


# DeclarativeBase声明式基类：sqlalchemy官方推荐的唯一基类
# 其他实体类都要继承base基类
class Base(DeclarativeBase):
    pass