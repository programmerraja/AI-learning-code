from transformers import AutoTokenizer, AutoModelForCausalLM

# 940MB
model_path = "ahxt/LiteLlama-460M-1T"

model = AutoModelForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
model.eval()

prompt = "abcdefgh"
input_ids = tokenizer(prompt, return_tensors="pt").input_ids
print(input_ids) 
# tokens = model.generate(input_ids, max_length=20)

# print(tokenizer.decode(tokens[0].tolist(), skip_special_tokens=True))

