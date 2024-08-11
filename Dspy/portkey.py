from portkey_ai import Portkey

portkey = Portkey(
    api_key="",  # Replace with your Portkey API key
    virtual_key="gemeni-2f24b9",  # Replace with your virtual key for Google
)

#  "x-portkey-api-key": "",
#         "x-portkey-virtual-id": "gemeni-2f24b9",
#         # "x-portkey-config":"pc-test-daf64c",
#         "x-portkey-provider":"google"

completion = portkey.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are not a helpful assistant"},
        {"role": "user", "content": "Say this is a test"},
    ],
    model="gemini-1.5-flash-001",
)

print(completion)
