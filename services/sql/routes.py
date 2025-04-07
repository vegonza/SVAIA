from flask import Blueprint
from .models import Project

sql_bp = Blueprint('sql', __name__)


@sql_bp.route('/projects/<string:uuid>', methods=['GET'])
def get_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if project is None or project.user != 'admin':
        return {'error': 'Project not found'}, 404
    return project.to_dict(), 200


@sql_bp.route('/projects', methods=['POST'])
def create_project():
    pass


@sql_bp.route('/projects/<string:uuid>', methods=['DELETE'])
def delete_project(uuid):
    pass
