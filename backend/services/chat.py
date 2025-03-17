from openai import OpenAI
import os


api_key = os.environ.get("AI_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def get_response(message: str):
    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-lite-preview-02-05:free",
        messages=[
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return completion.choices[0].message.content
