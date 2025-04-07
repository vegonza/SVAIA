import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from flask import Response, stream_with_context
import json

from services.sql.models import Message, db
from .prompts import SYSTEM_MESSAGE

load_dotenv(find_dotenv())

api_key = os.environ.get("AI_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def get_response(message: str, project_uuid: str = None):
    stream = client.chat.completions.create(
        model="google/gemini-2.0-flash-exp:free",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": message
            }
        ],
        stream=True
    )

    def generate():
        collected_chunks = []
        collected_content = ""

        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                collected_chunks.append(content)
                collected_content += content

                yield f"data: {json.dumps({'chunk': content, 'full_content': collected_content})}\n\n"

        if project_uuid:
            ai_message = Message(
                content=collected_content,
                is_user=False,
                project_uuid=project_uuid
            )
            db.session.add(ai_message)
            db.session.commit()

        yield f"data: {json.dumps({'done': True, 'full_content': collected_content})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')
