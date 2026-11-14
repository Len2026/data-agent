"""
提示词加载器
"""
from pathlib import Path

def load_prompt(file_name: str)->str:
    # 获取提示词文件路径
    prompt_path = Path(__file__).parents[2] / f'prompts/{file_name}'

    return prompt_path.read_text(encoding='utf-8')

if __name__ == '__main__':
    print(load_prompt('correct_sql.prompt'))