from langchain.chat_models import init_chat_model

from app.conf.app_config import app_config

llm = init_chat_model(
    model=app_config.llm.model_name,
    api_key=app_config.llm.api_key,
    temperature=0, # 表示确定性输出
    # model_provider=''
    # base_url=''
)

if __name__ == '__main__':
    for chunk in llm.stream('你是谁'):
        print(chunk.text, end='', flush=True)