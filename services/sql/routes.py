from flask import Blueprint
from .models import Project

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/projects/<string: uuid>', methods=['GET'])
def get_project(uuid):
    project = Project.query.filter_by(uuid=uuid).first()
    if project is None or project.user != 'admin':
        return {'error': 'Project not found'}, 404
    return project.to_dict(), 200


@auth_bp.route('/projects', methods=['POST'])
def create_project():
    pass


@auth_bp.route('/projects', methods=['DELETE'])
def delete_project():
    pass
