from uuid import uuid4

from flask import Blueprint, request

from .models import Message, Project, db

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/<string:uuid>', methods=['GET'])
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
def get_projects():
    projects = Project.query.all()
    return [project.to_dict() for project in projects]


@projects_bp.route('/', methods=['POST'])
def create_project():
    project = Project(
        uuid=str(uuid4()),
        name=request.json['name']
    )
    db.session.add(project)
    db.session.commit()
    return project.to_dict(), 200


@projects_bp.route('/<string:uuid>', methods=['DELETE'])
def delete_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    db.session.delete(project)
    db.session.commit()
    return {"message": "Project deleted successfully"}, 200
