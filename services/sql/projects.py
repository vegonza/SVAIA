from uuid import uuid4
from datetime import datetime

from flask import Blueprint, request
from flask_login import current_user, login_required

from libs.logging_utils import log_manager
from services.decorators import admin_required

from .models import Message, Project, db

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/<string:uuid>', methods=['GET'])
@login_required
def load_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    # get all messages of this proyect
    messages = Message.query.filter_by(project_uuid=uuid).order_by(Message.timestamp).all()

    response = project.to_dict()
    response['messages'] = [message.to_dict() for message in messages]

    return response


@projects_bp.route('/', methods=['GET'])
@login_required
def get_user_projects():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return [project.to_dict() for project in projects]


@projects_bp.route('/user/<int:user_id>', methods=['GET'])
@admin_required
def get_projects_by_user(user_id):
    projects = Project.query.filter_by(user_id=user_id).all()
    return [project.to_dict() for project in projects]


@projects_bp.route('/', methods=['POST'])
@login_required
def create_project():
    project = Project(
        uuid=str(uuid4()),
        name=request.json['name'],
        description=request.json.get('description', ''),
        user_id=current_user.id
    )
    db.session.add(project)
    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=create_project.__name__, argument=str(project.to_dict()), log_string="Project created successfully")    
    return project.to_dict(), 200


@projects_bp.route('/<string:uuid>', methods=['DELETE'])
@login_required
def delete_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        log_manager.add_log(log_level="warning", user=current_user.name, function=delete_project.__name__, argument=str(uuid), log_string="Project not found")
        return {"error": "Project not found"}, 404

    db.session.delete(project)
    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=delete_project.__name__, argument=str(project.to_dict()), log_string="Project deleted successfully")
    return {"message": "Project deleted successfully"}, 200


@projects_bp.route('/all', methods=['GET'])
@admin_required
def get_all_projects():
    projects = Project.query.all()
    return [project.to_dict() for project in projects]


@projects_bp.route('/<string:uuid>', methods=['PUT'])
@login_required
def update_project(uuid):
    project: Project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    if not current_user.is_admin and project.user_id != current_user.id:
        return {"error": "Unauthorized"}, 403

    data = request.json
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']

    project.updated_at = datetime.utcnow()
    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=update_project.__name__, argument=str(project.to_dict()), log_string="Project updated successfully")
    return project.to_dict()
