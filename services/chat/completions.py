import json
import os
from datetime import datetime
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from flask import Response, stream_with_context
from openai import OpenAI

from services.sql.models import Message, Project, db

from .prompts import SYSTEM_MESSAGE, FilesFormat
from .types import ChatMessage, File


load_dotenv(find_dotenv())

api_key = os.environ.get("AI_API_KEY")
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=api_key,
)

sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.4",
    "version": 1,
    "components": [
        {
            "type": "library",
            "name": "django",
            "version": "3.2.4",
            "purl": "pkg:pypi/django@3.2.4"
        },
        {
            "type": "library", 
            "name": "requests",
            "version": "2.26.0",
            "purl": "pkg:pypi/requests@2.26.0"
        },
        {
            "type": "library",
            "name": "numpy",
            "version": "1.19.5",
            "purl": "pkg:pypi/numpy@1.19.5"
        },
        {
            "type": "container",
            "name": "python",
            "version": "3.9-slim",
            "purl": "pkg:docker/python@3.9-slim"
        }
    ],
    "dependencies": [
        {
            "ref": "pkg:pypi/django@3.2.4",
            "dependsOn": []
        },
        {
            "ref": "pkg:pypi/requests@2.26.0",
            "dependsOn": []
        },
        {
            "ref": "pkg:pypi/numpy@1.19.5",
            "dependsOn": []
        }
    ]
}

def get_response(message: str, requisitos: str, history: list[ChatMessage], archivos: list[File], project_uuid: Optional[str] = None):
    archivos_str = FilesFormat(archivos)
    #llamada a funcion para obtener vulnerabilidades de CVE
    
    
    stream = client.chat.completions.create(
        model="gemini-2.5-flash-preview-05-20",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_MESSAGE.format(requisitos=requisitos, archivos=archivos_str)
            },
            *history,
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

            project: Project = Project.query.filter_by(uuid=project_uuid).first()
            if project:
                project.updated_at = datetime.utcnow()

            db.session.commit()

        yield f"data: {json.dumps({'done': True, 'full_content': collected_content})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')
