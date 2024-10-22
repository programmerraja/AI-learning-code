import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))


custom_model = genai.GenerativeModel("gemini-1.5-flash-001")

print(custom_model.generate_content("hai"))
