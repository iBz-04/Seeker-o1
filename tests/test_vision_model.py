import openai
import os
import base64
from dotenv import load_dotenv

load_dotenv()

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

openai.api_key = os.environ.get("OPENAI_API_KEY")

image_path = "assets/seeker_logo.png"
image_b64 = image_to_base64(image_path)

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        }
    ],
    max_tokens=300
)

print(response.choices[0].message.content)
