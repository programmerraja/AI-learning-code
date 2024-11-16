from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import base64
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmbeddingsRequest(BaseModel):
    model: str
    prompt: str
    options: Optional[Dict[str, Any]] = {}
    keep_alive: Optional[bool] = None

class GenerateRequest(BaseModel):
    model: str
    prompt: str
    suffix: Optional[str] = None
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[List[str]] = []
    stream: Optional[bool] = None
    raw: Optional[bool] = None
    images: Optional[List[str]] = []
    format: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}
    keep_alive: Optional[bool] = None

def _encode_image(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error encoding image: {str(e)}")

OLLAMA_BASE_URL = "http://localhost:11434"  # Adjust this to your Ollama server URL

@app.post("/api/embeddings")
async def create_embeddings(request: EmbeddingsRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": request.model,
                    "prompt": request.prompt,
                    "options": request.options,
                    "keep_alive": request.keep_alive
                }
            )
            response.raise_for_status()
            # {"embedding":[]}
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error calling Ollama API: {str(e)}")

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": request.model,
                    "prompt": request.prompt,
                    "suffix": request.suffix,
                    "system": request.system,
                    "template": request.template,
                    "context": request.context,
                    "stream": request.stream,
                    "raw": request.raw,
                    "images": request.images,
                    "format": request.format,
                    "options": request.options,
                    "keep_alive": request.keep_alive
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error calling Ollama API: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
