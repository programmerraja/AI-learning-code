from typing import List

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from helicone_async import HeliconeAsyncLogger
import os

os.environ["TRACELOOP_METRICS_ENABLED"] = "true"
os.environ["TRACELOOP_TRACING_ENABLED"] = "true"
os.environ["TRACELOOP_LOGGING_ENABLED"] = "true"


# from openai import OpenAI

logger = HeliconeAsyncLogger(
    api_key="",
)

logger.init()


@tool
def validate_user(user_id: int, addresses: List[str]) -> bool:
    """Validate user using historical addresses.

    Args:
        user_id (int): the user ID.
        addresses (List[str]): Previous addresses as a list of strings.
    """
    return True


llm = ChatOllama(
    model="gemma",
    temperature=0,
)

result = llm.invoke("hi.")
# result.tool_calls
