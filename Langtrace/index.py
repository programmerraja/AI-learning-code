from langtrace_python_sdk import langtrace  # Must precede any llm module imports
import google.generativeai as genai
import json
from langtrace_python_sdk import get_prompt_from_registry
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))

langtrace.init(api_key=os.getenv("LANGTRACE_API_kEY"))

model = genai.GenerativeModel("gemini-1.5-flash-001")
# response = model.generate_content("The opposite of hot is")

# print(response.text)


# Paste this code after your langtrace init function
response = get_prompt_from_registry(
    "clzqa5c6g00013gw5354538j0",
    options={"variables": {"hai": "Healthcare"}},
    api_key=os.getenv("LANGTRACE_API_kEY"),
)

# for json prompts (ex: tool calling)
# prompt = json.loads(prompt)
prompt = response["value"]
print(prompt)
