from langchain.chat_models.base import BaseChatModel
import os
from langchain_community.chat_models import ChatAnthropic
from langchain_openai import ChatOpenAI  # Updated import

def get_llm() -> BaseChatModel:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    match provider:
        case "openai":
            return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), 
                              api_key=os.getenv("OPENAI_API_KEY"))
        case "anthropic":
            return ChatAnthropic(model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"), 
                                 anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
        case _:
            raise ValueError(f"Unsupported provider '{provider}' configured.")