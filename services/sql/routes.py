from uuid import uuid4

from flask import Blueprint, request

from .models import Project, db

sql_bp = Blueprint('sql', __name__)


@sql_bp.route('/projects/<string:uuid>', methods=['GET'])
def load_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404
    return project.to_dict()


@sql_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return [project.to_dict() for project in projects]


@sql_bp.route('/projects', methods=['POST'])
def create_project():
    project = Project(
        uuid=str(uuid4()),
        name=request.json['name']
    )
    db.session.add(project)
    db.session.commit()
    return project.to_dict(), 200


@sql_bp.route('/projects/<string:uuid>', methods=['DELETE'])
def delete_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    db.session.delete(project)
    db.session.commit()
    return {"message": "Project deleted successfully"}, 200
