import requests


def llm_request_with_tools(prompt, tools=None):
    """
    Sends a request to the LLM API, passing tools and prompt as inputs.

    Args:
        prompt (str): The text prompt to send to the LLM.
        tools (dict, optional): Tooling-specific data to include in the LLM request.

    Returns:
        dict: JSON response from the LLM API.
    """
    url = "http://127.0.0.1:8080/completion"
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    }

    # Prepare the payload with tools and prompt
    payload = {
        "stream": False,
        "n_predict": 400,
        "temperature": 0.7,
        "stop": ["</s>", "Llama:", "User:"],
        "repeat_last_n": 1385,
        "repeat_penalty": 1.07,
        "top_k": 40,
        "top_p": 0.82,
        "min_p": 0.05,
        "tfs_z": 1,
        "typical_p": 1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "mirostat": 0,
        "mirostat_tau": 5,
        "mirostat_eta": 0.1,
        "grammar": "",
        "n_probs": 0,
        "min_keep": 0,
        "image_data": [],
        "cache_prompt": True,
        "api_key": "",
        "slot_id": -1,
        "prompt": prompt,
        "tools": tools if tools else {},
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response)
    # Handle the response
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to connect to LLM. Status: {response.status_code}, Response: {response.text}"
        )


# Example usage
tools_payload = {
    "calculator": {
        "enabled": True,
        "inputs": {"operation": "addition", "operands": [5, 7]},
    }
}

prompt = "This is a conversation between User and Llama, a helpful chatbot. Perform a calculation using the provided tool."

response = llm_request_with_tools(prompt, tools=tools_payload)
print(response)
