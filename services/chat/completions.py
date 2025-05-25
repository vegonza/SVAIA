import json
import os
from datetime import datetime
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from flask import Response, stream_with_context
from openai import OpenAI
from swarm import Swarm

from services.sql.models import Message, Project, db

from .agent_manager import cve_agent
from .prompts import SYSTEM_MESSAGE, FilesFormat
from .types import ChatMessage, File

load_dotenv(find_dotenv())

client = Swarm(OpenAI(base_url="https://openrouter.ai/api/v1",
               api_key=os.environ["AI_API_KEY"]))

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
    stream = client.run_and_stream(
        agent=cve_agent,
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
    )

    def generate():
        collected_content = ""

        already_calling = False
        for chunk in stream:
            content = chunk.get('content')
            error = chunk.get('error')
            if error:
                data = f"data: {json.dumps({'type': 'error', 'content': error})}\n\n"
                yield data

            if content:
                already_calling = False
                data = f"data: {json.dumps({'type': 'text', 'content': content})}\n\n"
                collected_content += content
                yield data

            tools = chunk.get('tool_calls')
            if tools:
                for tool in tools:
                    function = tool.get('function', {})
                    if name := function.get("name"):
                        if not already_calling:
                            already_calling = True
                            data = f"data: {json.dumps({'type': 'tool_call', 'tool_name': name})}\n\n"
                            yield data

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
