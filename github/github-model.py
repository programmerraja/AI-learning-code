import openai, os

client = openai.OpenAI(
    api_key=os.environ["GITHUB_TOKEN"], base_url="https://models.inference.ai.azure.com"
)
print(client.chat.completions.create("Hai"))
