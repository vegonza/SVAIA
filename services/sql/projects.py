from uuid import uuid4
from datetime import datetime
import subprocess
import json
import tempfile
import os

from flask import Blueprint, request
from flask_login import current_user, login_required

from libs.logging_utils import log_manager
from services.decorators import admin_required

from .models import Dockerfile, DockerCompose, SoftwareBillOfMaterials, Message, Project, db

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
        total_vulnerabilities_criteria=request.json.get('total_vulnerabilities_criteria'),
        solvability_criteria=request.json.get('solvability_criteria'),
        max_vulnerability_level=request.json.get('max_vulnerability_level'),
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
    if 'total_vulnerabilities_criteria' in data:
        project.total_vulnerabilities_criteria = data['total_vulnerabilities_criteria']
    if 'solvability_criteria' in data:
        project.solvability_criteria = data['solvability_criteria']
    if 'max_vulnerability_level' in data:
        project.max_vulnerability_level = data['max_vulnerability_level']

    project.updated_at = datetime.utcnow()
    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=update_project.__name__, argument=str(project.to_dict()), log_string="Project updated successfully")
    return project.to_dict()


@projects_bp.route('/upload/dockerfiles/<string:uuid>', methods=['POST'])
@login_required
def upload_dockerfiles(uuid):
    project: Project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    dockerfiles = request.files.getlist('dockerfiles')
    if not dockerfiles:
        return {"error": "Dockerfiles not found"}, 400

    for dockerfile in dockerfiles:
        dockerfile_content = dockerfile.read().decode('utf-8')
        project.dockerfiles.append(Dockerfile(content=dockerfile_content))

    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=upload_dockerfiles.__name__, argument=str(project.to_dict()), log_string="Dockerfiles uploaded successfully")
    return {"message": "Dockerfiles uploaded successfully"}, 200


@projects_bp.route('/upload/docker-compose-files/<string:uuid>', methods=['POST'])
@login_required
def upload_docker_compose_files(uuid):
    project: Project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    docker_composes = request.files.getlist('docker_compose_files')
    if not docker_composes:
        return {"error": "Docker compose files not found"}, 400

    for docker_compose in docker_composes:
        docker_compose_content = docker_compose.read().decode('utf-8')
        project.docker_composes.append(DockerCompose(content=docker_compose_content))

    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=upload_docker_compose_files.__name__,
                        argument=str(project.to_dict()), log_string="Docker compose files uploaded successfully")
    return {"message": "Docker compose files uploaded successfully"}, 200


def generate_sbom(tar_image_path: str) -> dict:
    result = subprocess.run(
        ["syft", tar_image_path, "-o", "cyclonedx-json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True
    )
    return json.loads(result.stdout)


@projects_bp.route('/upload/docker-image/<string:uuid>', methods=['POST'])
@login_required
def upload_docker_image(uuid: str):
    project: Project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    images = request.files.getlist('images')
    if not images:
        return {"error": "Images not found"}, 400

    for image in images:
        with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name
        try:
            sbom = generate_sbom(tmp_path)
            project.sboms.append(SoftwareBillOfMaterials(content=json.dumps(sbom)))
        finally:
            os.remove(tmp_path)

    db.session.commit()
    log_manager.add_log(log_level="info", user=current_user.name, function=upload_docker_image.__name__, argument=str(project.to_dict()), log_string="Docker images uploaded and SBOMs generated")
    return {"message": "Docker images uploaded and SBOMs generated"}, 200
