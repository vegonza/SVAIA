from datetime import datetime, timezone

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from libs.logging_utils import log_manager
from services.sql.models import Message, Project, db

from .completions import (get_analysis_response, get_cve_agent_response,
                          get_mermaid_response)
from .utils import collect_project_files, get_project_criteria

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

    if not project_uuid:
        return jsonify({"error": "missing project_uuid"}), 400

    project: Project = Project.query.filter_by(uuid=project_uuid).first()
    if not project:
        return jsonify({"error": "project not found"}), 404

    Message.query.filter_by(project_uuid=project_uuid).delete()

    project.updated_at = datetime.now(datetime.UTC)
    db.session.commit()

    files = collect_project_files(project)

    return get_mermaid_response(files, project_uuid)


@chat_bp.route("/analyze-project", methods=["POST"])
def analyze_project():
    data: dict = request.json
    project_uuid = data.get("project_uuid")

    if not project_uuid:
        return jsonify({"error": "missing project_uuid"}), 400

    project: Project = Project.query.filter_by(uuid=project_uuid).first()
    if not project:
        return jsonify({"error": "project not found"}), 404

    project.updated_at = datetime.now(datetime.UTC)
    db.session.commit()

    files = collect_project_files(project)

    return get_analysis_response(
        files=files,
        project_uuid=project_uuid,
        project_name=project.name,
        project_description=project.description,
        project_criteria=get_project_criteria(project)
    )


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

    project.updated_at = datetime.now(datetime.UTC)
    db.session.commit()

    history = Message.query.filter_by(project_uuid=project_uuid).order_by(Message.timestamp).all()
    history_dicts = [{"role": "user" if msg.is_user else "assistant", "content": msg.content} for msg in history]

    log_manager.add_log(
        log_level="debug",
        user="system",
        function="completion",
        argument=f"message={message}, history={history_dicts}, files={collect_project_files(project)}, project_uuid={project_uuid}, project_name={project.name}, project_description={project.description}, project_criteria={get_project_criteria(project)}",
        log_string="Completion request received"
    )
    return get_cve_agent_response(
        message=message,
        history=history_dicts,
        files=collect_project_files(project),
        project_uuid=project_uuid,
        project_name=project.name,
        project_description=project.description,
        project_criteria=get_project_criteria(project)
    )
