from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

import instructor


class Character(BaseModel):
    name: str
    age: int
    fact: List[str] = Field(..., description="A list of facts about the character")


client = instructor.from_openai(
    OpenAI(
        base_url="",
        api_key="ollama",  
    ),
    mode=instructor.Mode.JSON,
)

resp = client.chat.completions.create(
    model="tinyllama",
    messages=[
        {
            "role": "user",
            "content": "Tell me about the Harry Potter",
        }
    ],
    response_model=Character,
)
print(resp.model_dump_json(indent=2))
