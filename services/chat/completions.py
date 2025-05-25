import json
import os
from datetime import datetime
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from flask import Response, stream_with_context
from openai import OpenAI
from tide_swarm import Swarm

from services.sql.models import Message, Project, db

from .agent_manager import analysis_agent, cve_agent, mermaid_agent
from .prompts import FilesFormat
from .types import ChatMessage, File

load_dotenv(find_dotenv())

client = Swarm(
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["AI_API_KEY"]
    )
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


def generate(stream, project_uuid: Optional[str]):
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


# ---------------- generator wrappers ---------------- #
def get_cve_agent_response(message: str, history: list[ChatMessage], files: list[File], project_uuid: Optional[str], project_name: str, project_description: str, project_criteria: dict):
    stream = client.run_and_stream(
        agent=cve_agent,
        context_variables={
            "project_name": project_name,
            "project_description": project_description,
            "project_criteria": project_criteria,
            "files": files
        },
        messages=[
            *history,
            {
                "role": "user",
                "content": message
            }
        ],
    )

    return Response(stream_with_context(generate(stream, project_uuid)), mimetype='text/event-stream')


def get_mermaid_response(files: list[File], project_uuid: Optional[str]):
    docker_compose_content = ""
    for file in files:
        if file["name"] == "docker-compose.yml":
            docker_compose_content = file["content"]
            break

    if not docker_compose_content:
        docker_compose_content = "No docker-compose.yml file found in the project."

    stream = client.run_and_stream(
        agent=mermaid_agent,
        context_variables={
            "files": files
        },
        messages=[
            {
                "role": "user",
                "content": "Analiza el contenido de mis archivos y genera un diagrama"
            }
        ],
    )

    return Response(stream_with_context(generate(stream, project_uuid)), mimetype='text/event-stream')


def get_analysis_response(files: list[File], project_uuid: Optional[str], project_name: str, project_description: str, project_criteria: dict):
    stream = client.run_and_stream(
        agent=analysis_agent,
        context_variables={
            "project_name": project_name,
            "project_description": project_description,
            "project_criteria": project_criteria,
            "files": files
        },
        messages=[
            {
                "role": "user",
                "content": f"This are my files:\n{FilesFormat(files)}"
            }
        ],
    )

    return Response(stream_with_context(generate(stream, project_uuid)), mimetype='text/event-stream')
