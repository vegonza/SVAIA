from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required

from services.sql.models import Message, Project, db

from .completions import get_response

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
@login_required
def index():
    return render_template("chat.html")


@chat_bp.route("/completion", methods=["POST"])
@login_required
def completion():
    data = request.json
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
    if project:
        project.updated_at = datetime.utcnow()

    db.session.commit()

    history = Message.query.filter_by(project_uuid=project_uuid).order_by(Message.timestamp).all()
   
    history_dicts = [{"role": "user" if msg.is_user else "assistant", "content": msg.content} for msg in history]

    requirements = f"project_solvability_criteria: {project.solvability_criteria}\nproject_max_vulnerability_level: {project.max_vulnerability_level}\nproject_total_vulnerabilities_criteria: {project.total_vulnerabilities_criteria}"

    return get_response(
        message=message,
        user_name="",
        history=history_dicts,
        archivos=[],
        project_uuid=project_uuid,
        project_name=project.name,
        project_description=project.description,
        requisitos=requirements
    )

