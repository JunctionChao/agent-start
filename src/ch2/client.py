import os
from typing import List, Dict

from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger


# 加载 .env 文件中的环境变量
load_dotenv()

class LLMClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("MODEL_ID")
        apiKey = apiKey or os.getenv("API_KEY")
        baseUrl = baseUrl or os.getenv("BASE_URL")
        timeout = timeout or int(os.getenv("TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        logger.info(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            
            # 处理流式响应
            logger.info("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except Exception as e:
            logger.error(f"❌ 调用LLM API时发生错误: {e}")
            return None

# --- 客户端使用示例 ---
if __name__ == '__main__':
    try:
        llmClient = LLMClient()
        
        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]
        
        logger.debug("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            logger.debug("--- 完整模型响应 ---")
            print(responseText)

    except ValueError as e:
        logger.error(e)
