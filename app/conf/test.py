from dataclasses import dataclass
from pathlib import Path

import yaml
from omegaconf import OmegaConf

# 获取yaml文件的路径
yaml_path = Path(__file__).parents[2] / 'conf/test.yaml'
# print(yaml_path) # E:\workspaces\data-agent\conf\test.yaml


# 读取yaml文件中的内容
# with open(yaml_path, 'r',encoding='utf-8') as file:
#     yaml_data = file.read()
#     print(yaml_data) # str

# with open(yaml_path, 'r', encoding='utf-8') as file:
#     yaml_data = yaml.safe_load(file)
#     print(yaml_data) # {'name': '张三', 'age': 23, 'sex': '男'}
#     print(yaml_data['name']) # 张三
    # 问题：
    # 1.读取到的yaml数据为字典格式，不能通过 对象.属性名 方式访问数据
    # 2.访问对象属性时，IDE没有提示


# 使用OmegaConf插件读取yaml配置内容

# 定义数据类（数据模型）
@dataclass
class Person:
    name: str
    age: int
    sex: str

# 读取yaml文件中的内容
yaml_data = OmegaConf.load(yaml_path)
# print(yaml_data) # {'name': '张三', 'age': 23, 'sex': '男'}

person: Person = OmegaConf.to_object(OmegaConf.merge(Person,yaml_data))
print(person) # Person(name='张三', age=23, sex='男')
print(person.name) # 张三