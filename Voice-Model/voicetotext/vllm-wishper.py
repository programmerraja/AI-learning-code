from vllm.assets.audio import AudioAsset
from vllm import LLM, SamplingParams

# prepare model
llm = LLM(
    model="neuralmagic/whisper-large-v2-W4A16-G128",
    max_model_len=448,
    max_num_seqs=400,
    limit_mm_per_prompt={"audio": 1},
)

# prepare inputs
inputs = {  # Test explicit encoder/decoder prompt
    "encoder_prompt": {
        "prompt": "",
        "multi_modal_data": {
            "audio": AudioAsset("winning_call").audio_and_sample_rate,
        },
    },
    "decoder_prompt": "<|startoftranscript|>",
}

# generate response
print("========== SAMPLE GENERATION ==============")
outputs = llm.generate(inputs, SamplingParams(temperature=0.0, max_tokens=64))
print(f"PROMPT  : {outputs[0].prompt}")
print(f"RESPONSE: {outputs[0].outputs[0].text}")
print("==========================================")
