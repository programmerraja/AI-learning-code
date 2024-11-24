from llama_index.core.tools import FunctionTool
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import AgentRunner
from llama_index.agent.openai import OpenAIAgentWorker


# define sample Tool
def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)

# initialize llm
# llm = OpenAI(model="gpt-3.5-turbo-0613")
llm = Ollama(model="gemma", request_timeout=120.0)

# initialize ReAct agent
agent = AgentRunner.from_llm([multiply_tool], llm=llm, verbose=True)

print(agent.chat("What is 2123 * 215123"))
