from huggingface_hub import InferenceClient
import os

messages = [{"role": "user", "content": "What is the capital of France?"}]
client = InferenceClient(
    "w601sxs/b1ade-embed", token=os.getenv("HUGGING_FACE_TOKE")
)
# print(client.chat_completion(messages, max_tokens=100).choices[0].message.content)

# feature_extraction -> will return embedding
print(client.feature_extraction(text="hai"))


