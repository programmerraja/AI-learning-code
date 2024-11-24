from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
import os

from llama_index.llms.ollama import Ollama
from llama_index.core import set_global_handler

# Make sure you've installed the 'llama-index-callbacks-langfuse' integration package.

# NOTE: Set your environment variables 'LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY' and 'LANGFUSE_HOST'
# as shown in your langfuse.com project settings.


set_global_handler("langfuse")


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    llm = Ollama(model="gemma", request_timeout=120.0)

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        print("response", response)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        print("response", response)
        return StopEvent(result=str(response))


w = JokeFlow(timeout=1000000, verbose=True)


async def main():
    result = await w.run(topic="pirates")
    print(str(result))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


# llm = Ollama(model="gemma", request_timeout=120.0)
# print(llm.complete("hia"))
