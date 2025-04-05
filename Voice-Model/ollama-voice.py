import os
import sys
import requests
import json
import time
import wave
import numpy as np
import sounddevice as sd
import argparse
import threading
import queue
import asyncio

# Ollama API settings
API_URL = "http://127.0.0.1:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}

proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}
# Model parameters
MAX_TOKENS = 1200
TEMPERATURE = 0.6
TOP_P = 0.9
REPETITION_PENALTY = 1.1
SAMPLE_RATE = 24000

# Available voices
AVAILABLE_VOICES = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]
DEFAULT_VOICE = "tara"


def format_prompt(prompt, voice=DEFAULT_VOICE):
    """Format prompt for the model with voice prefix."""
    if voice not in AVAILABLE_VOICES:
        print(
            f"Warning: Voice '{voice}' not recognized. Using '{DEFAULT_VOICE}' instead."
        )
        voice = DEFAULT_VOICE
    return f"{voice}: {prompt}"


def generate_tokens_from_ollama(prompt, voice=DEFAULT_VOICE):
    """Generate text from Ollama API."""
    formatted_prompt = format_prompt(prompt, voice)
    payload = {
        "model": "hf.co/isaiahbjork/orpheus-3b-0.1-ft-Q4_K_M-GGUF:latest",
        "prompt": formatted_prompt,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "repeat_penalty": REPETITION_PENALTY,
        "stream": True,
    }
    print(formatted_prompt)
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        stream=True,
        proxies=proxies,
    )
    if response.status_code != 200:
        print(f"Error: API request failed with status {response.status_code}")
        print(response.text)
        return
    for line in response.iter_lines():
        print(line, "line")
        if line:
            try:
                data = json.loads(line)
                if "text" in data:
                    yield data["text"]
            except json.JSONDecodeError:
                continue


def text_to_speech(text, output_file):
    """Convert text to speech (placeholder for actual TTS processing)."""
    print(f"[TTS] Converting text to speech: {text[:50]}...")
    with open(output_file, "w") as f:
        f.write(text)


def generate_speech_from_ollama(prompt, voice=DEFAULT_VOICE, output_file=None):
    """Generate speech from text using Ollama."""
    output_text = "".join(generate_tokens_from_ollama(prompt, voice))
    if output_file:
        text_to_speech(output_text, output_file)
    else:
        print(output_text)


def main():
    parser = argparse.ArgumentParser(description="Ollama TTS Script")
    parser.add_argument("--text", type=str, help="Text to convert to speech")
    parser.add_argument(
        "--voice", type=str, default=DEFAULT_VOICE, help="Voice selection"
    )
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()
    if not args.text:
        args.text = input("Enter text to synthesize: ")
    output_file = args.output if args.output else "output.wb"
    generate_speech_from_ollama(args.text, args.voice, output_file)
    print(f"Generated speech saved to {output_file}")


if __name__ == "__main__":
    main()
