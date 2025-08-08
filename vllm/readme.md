docker build -f docker/Dockerfile.cpu --tag vllm-cpu-env --target vllm-openai .

docker run --rm \
             --privileged=true \
             --shm-size=4g \
             -p 8000:8000 \
             vllm-cpu-env \
             --model=microsoft/bitnet-b1.58-2B-4T \
             --trust-remote-code
             --dtype=bfloat16 
             