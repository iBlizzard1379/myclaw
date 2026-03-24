
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, OPENAI_API_KEY, OPENAI_BASE_URL, ANTHROPIC_API_KEY, \
    ANTHROPIC_BASE_URL, BAILIAN_API_KEY, BAILIAN_BASE_URL_OPENAI, ZHIPUAI_API_KEY, ZHIPUAI_BASE_URL

deepseek_llm: BaseChatModel | None = (
    init_chat_model(
        model="deepseek-chat", model_provider="deepseek",
        api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL,
    ) if DEEPSEEK_API_KEY else None
)

openai_llm: BaseChatModel | None = (
    init_chat_model(
        model="gpt-5.4-mini", model_provider="openai",
        api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL,
    ) if OPENAI_API_KEY else None
)

bailian_llm: BaseChatModel | None = (
    init_chat_model(
        model="qwen3.5-plus", model_provider="openai",
        api_key=BAILIAN_API_KEY, base_url=BAILIAN_BASE_URL_OPENAI,
    ) if BAILIAN_API_KEY else None
)

zhipu_llm: BaseChatModel | None = (
    init_chat_model(
        model="glm-4-plus", model_provider="openai",
        api_key=ZHIPUAI_API_KEY, base_url=ZHIPUAI_BASE_URL,
    ) if ZHIPUAI_API_KEY else None
)

# anthropic_llm = init_chat_model(
#     model="claude-3-5-haiku-latest",
#     model_provider="anthropic",
#     api_key=ANTHROPIC_API_KEY,
#     base_url=ANTHROPIC_BASE_URL,
# )

# ollama_llm = init_chat_model(
#     model="deepseek-r1:1.5b",
#     model_provider="ollama",
#     base_url="http://192.168.1.106:11434",
# )