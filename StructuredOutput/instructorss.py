# import google.auth
# import google.auth.transport.requests
# import instructor
# from openai import OpenAI
# from pydantic import BaseModel
# from dotenv import load_dotenv
# load_dotenv()

# creds, project = google.auth.default()

# auth_req = google.auth.transport.requests.Request()
# creds.refresh(auth_req)

# # Pass the Vertex endpoint and authentication to the OpenAI SDK
# PROJECT = 'PROJECT_ID'
# LOCATION = (
#     'LOCATION'  # https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations
# )
# base_url = f'https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/{LOCATION}/endpoints/openapi'

# client = instructor.from_openai(
#     OpenAI(base_url=base_url, api_key=creds.token), mode=instructor.Mode.JSON
# )

# # JSON mode is req'd
# class User(BaseModel):
#     name: str
#     age: int


# resp = client.chat.completions.create(
#     model="google/gemini-1.5-flash-001",
#     max_tokens=1024,
#     messages=[
#         {
#             "role": "user",
#             "content": "Extract Jason is 25 years old.",
#         }
#     ],
#     response_model=User,
# )

# assert isinstance(resp, User)
# assert resp.name == "Jason"
# assert resp.age == 25