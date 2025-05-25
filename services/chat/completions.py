import json
import os
from datetime import datetime
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from flask import Response, stream_with_context
from openai import OpenAI
from swarm import Swarm

from services.sql.models import Message, Project, db

from .agent_manager import cve_agent, mermaid_agent
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


def get_response(message: str, user_name: str, history: list[ChatMessage], archivos: list[File], project_uuid: Optional[str], project_name: str, project_description: str, requisitos: str):
    criteria_lines = requisitos.split('\n')
    solvability_criteria = ""
    max_vulnerability_level = ""
    total_vulnerabilities_criteria = ""

    for line in criteria_lines:
        if line.startswith("project_solvability_criteria:"):
            solvability_criteria = line.replace("project_solvability_criteria:", "").strip()
        elif line.startswith("project_max_vulnerability_level:"):
            max_vulnerability_level = line.replace("project_max_vulnerability_level:", "").strip()
        elif line.startswith("project_total_vulnerabilities_criteria:"):
            total_vulnerabilities_criteria = line.replace("project_total_vulnerabilities_criteria:", "").strip()

    # Manejar valores nulos o vacíos con mensajes amigables
    if not solvability_criteria or solvability_criteria == "None":
        solvability_criteria = "No especificado"
    if not max_vulnerability_level or max_vulnerability_level == "None":
        max_vulnerability_level = "No especificado"
    if not total_vulnerabilities_criteria or total_vulnerabilities_criteria == "None":
        total_vulnerabilities_criteria = "No especificado"

    # Traducir los criterios de solvability a textos más descriptivos
    if solvability_criteria == "solvable":
        solvability_criteria = "Solo vulnerabilidades solucionables"
    elif solvability_criteria == "non_solvable":
        solvability_criteria = "Permitir vulnerabilidades no solucionables"
    elif solvability_criteria == "any":
        solvability_criteria = "Sin restricciones de solucionabilidad"

    stream = client.run_and_stream(
        agent=cve_agent,
        messages=[
            *history,
            {
                "role": "user",
                "content": message
            }
        ],
    )

    return Response(stream_with_context(generate(stream, project_uuid)), mimetype='text/event-stream')


def get_cve_agent_response(message: str, requisitos: str, history: list[ChatMessage], archivos: list[File], project_uuid: Optional[str]):
    stream = client.run_and_stream(
        agent=cve_agent,
        context_variables={
            "requisitos": requisitos,
            "archivos": archivos
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


def get_mermaid_response(archivos: list[File], project_uuid: Optional[str]):
    docker_compose_content = ""
    for archivo in archivos:
        if archivo["name"] == "docker-compose.yml":
            docker_compose_content = archivo["content"]
            break

    if not docker_compose_content:
        docker_compose_content = "No docker-compose.yml file found in the project."

    stream = client.run_and_stream(
        agent=mermaid_agent,
        context_variables={
            "archivos": archivos
        },
        messages=[
            {
                "role": "user",
                "content": "Analiza el contenido de mis archivos y genera un diagrama"
            }
        ],
    )

    return Response(stream_with_context(generate(stream, project_uuid)), mimetype='text/event-stream')
