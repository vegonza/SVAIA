from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from services.sql.models import Message, Project, db

from .completions import get_cve_agent_response, get_mermaid_response
from .types import File

chat_bp = Blueprint("chat", __name__)


@login_required
def before_request():
    pass


@chat_bp.route("/")
def index():
    return render_template("chat.html")


@chat_bp.route("/init-project", methods=["POST"])
def init_project():
    data: dict = request.json
    project_uuid = data.get("project_uuid")
    error_info = data.get("error_info")

    if not project_uuid:
        return jsonify({"error": "missing project_uuid"}), 400

    project: Project = Project.query.filter_by(uuid=project_uuid).first()
    if not project:
        return jsonify({"error": "project not found"}), 404

    project.updated_at = datetime.utcnow()
    db.session.commit()

    # Collect all project files
    archivos = []

    # Add dockerfiles
    for dockerfile in project.dockerfiles:
        archivos.append(File(
            name=f"dockerfile_{dockerfile.id}",
            content=dockerfile.content
        ))

    # Add docker-compose files
    for docker_compose in project.docker_composes:
        archivos.append(File(
            name="docker-compose.yml",
            content=docker_compose.content
        ))

    # Add SBOMs
    for sbom in project.sboms:
        archivos.append(File(
            name=f"sbom_{sbom.id}.json",
            content=sbom.content
        ))

    return get_mermaid_response(archivos, project_uuid, error_info)


@chat_bp.route("/completion", methods=["POST"])
def completion():
    data: dict = request.json
    message = data.get("message")
    project_uuid = data.get("project_uuid")

    if not message:
        return jsonify({"error": "missing message"}), 400

    if not project_uuid:
        return jsonify({"error": "missing project_uuid"}), 400

    user_message = Message(
        content=message,
        is_user=True,
        project_uuid=project_uuid
    )
    db.session.add(user_message)

    project: Project = Project.query.filter_by(uuid=project_uuid).first()
    if not project:
        return jsonify({"error": "project not found"}), 404

    project.updated_at = datetime.utcnow()
    db.session.commit()

    history = Message.query.filter_by(project_uuid=project_uuid).order_by(Message.timestamp).all()

    history_dicts = [{"role": "user" if msg.is_user else "assistant", "content": msg.content} for msg in history]

    requirements = f"project_solvability_criteria: {project.solvability_criteria}\nproject_max_vulnerability_level: {project.max_vulnerability_level}\nproject_total_vulnerabilities_criteria: {project.total_vulnerabilities_criteria}"

    return get_cve_agent_response(
        message=message,
        user_name="",
        history=history_dicts,
        archivos=[],
        project_uuid=project_uuid,
        project_name=project.name,
        project_description=project.description,
        requisitos=requirements
    )
