from dotenv import load_dotenv
load_dotenv()

import openai
import os

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    api_key = input("Enter your OpenAI API key: ")

client = openai.OpenAI(api_key=api_key)

try:
    # Test 1: Nike-like swoosh
    response1 = client.images.generate(
        prompt="A simple abstract swoosh logo, white on black background, minimal graphic art",
        n=1,
        size="1024x1024"
    )
    print("Nike-like swoosh Image URL:", response1.data[0].url)

    # Test 2: Mountain bike rider
    response2 = client.images.generate(
        prompt="A person riding a mountain bike on a scenic trail, digital art",
        n=1,
        size="1024x1024"
    )
    print("Mountain bike Image URL:", response2.data[0].url)
except Exception as e:
    print("Error generating image:", e)
