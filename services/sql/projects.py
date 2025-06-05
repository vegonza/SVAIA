from uuid import uuid4
from datetime import datetime
import subprocess
import json
import tempfile
import os
from typing import Any

from flask import Blueprint, request
from flask_login import current_user, login_required
from typeguard import typechecked

from libs.logging_utils import log_manager
from services.decorators import admin_required

from .models import Dockerfile, DockerCompose, SoftwareBillOfMaterials, Message, Project, db

projects_bp = Blueprint('projects', __name__)


@typechecked
def generate_sbom(tar_image_path: str) -> dict[str, Any]:
    result = subprocess.run(
        ["syft", tar_image_path, "-o", "cyclonedx-json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True
    )
    return json.loads(result.stdout)


@projects_bp.route('/<string:uuid>', methods=['GET'])
@login_required
def load_project(uuid: str):
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
def get_projects_by_user(user_id: int):
    projects = Project.query.filter_by(user_id=user_id).all()
    return [project.to_dict() for project in projects]


@projects_bp.route('/', methods=['POST'])
@login_required
def create_project():
    if 'name' not in request.form:
        return {"error": "Project name is required"}, 400

    docker_composes = request.files.getlist('docker_compose_files')
    if not docker_composes:
        return {"error": "At least one docker compose file is required"}, 400

    project = Project(
        uuid=str(uuid4()),
        name=request.form['name'],
        description=request.form.get('description', ''),
        total_vulnerabilities_criteria=request.form.get('total_vulnerabilities_criteria'),
        solvability_criteria=request.form.get('solvability_criteria'),
        max_vulnerability_level=request.form.get('max_vulnerability_level'),
        user_id=current_user.id
    )

    has_docker_composes = False
    has_dockerfiles = False
    has_images = False

    for docker_compose in docker_composes:
        docker_compose_content = docker_compose.read().decode('utf-8')
        project.docker_composes.append(DockerCompose(content=docker_compose_content))
        has_docker_composes = True

    dockerfiles = request.files.getlist('dockerfiles')
    for dockerfile in dockerfiles:
        dockerfile_content = dockerfile.read().decode('utf-8')
        project.dockerfiles.append(Dockerfile(content=dockerfile_content))
        has_dockerfiles = True

    images = request.files.getlist('images')
    for image in images:
        with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name
        try:
            sbom = generate_sbom(tmp_path)
            project.sboms.append(SoftwareBillOfMaterials(content=json.dumps(sbom)))
            has_images = True
        finally:
            os.remove(tmp_path)

    db.session.add(project)
    db.session.commit()

    if has_docker_composes:
        log_manager.add_log(log_level="info", user=current_user.name, function=create_project.__name__, argument=str(project.to_dict()), log_string="Docker compose files uploaded successfully")

    if has_dockerfiles:
        log_manager.add_log(log_level="info", user=current_user.name, function=create_project.__name__, argument=str(project.to_dict()), log_string="Dockerfiles uploaded successfully")

    if has_images:
        log_manager.add_log(log_level="info", user=current_user.name, function=create_project.__name__, argument=str(project.to_dict()), log_string="Docker images uploaded and SBOMs generated")

    log_manager.add_log(log_level="info", user=current_user.name, function=create_project.__name__, argument=str(project.to_dict()), log_string="Project created successfully")
    return project.to_dict(), 201


@projects_bp.route('/<string:uuid>', methods=['DELETE'])
@login_required
def delete_project(uuid: str):
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
def update_project(uuid: str):
    project: Project = Project.query.filter_by(uuid=uuid).first()
    if not project:
        return {"error": "Project not found"}, 404

    if not current_user.is_admin and project.user_id != current_user.id:
        return {"error": "Unauthorized"}, 403

    if 'name' in request.form:
        project.name = request.form['name']
    if 'description' in request.form:
        project.description = request.form['description']
    if 'total_vulnerabilities_criteria' in request.form:
        project.total_vulnerabilities_criteria = request.form['total_vulnerabilities_criteria']
    if 'solvability_criteria' in request.form:
        project.solvability_criteria = request.form['solvability_criteria']
    if 'max_vulnerability_level' in request.form:
        project.max_vulnerability_level = request.form['max_vulnerability_level']

    docker_composes = request.files.getlist('docker_compose_files')
    for docker_compose in docker_composes:
        docker_compose_content = docker_compose.read().decode('utf-8')
        project.docker_composes.append(DockerCompose(content=docker_compose_content))

    dockerfiles = request.files.getlist('dockerfiles')
    for dockerfile in dockerfiles:
        dockerfile_content = dockerfile.read().decode('utf-8')
        project.dockerfiles.append(Dockerfile(content=dockerfile_content))

    images = request.files.getlist('images')
    for image in images:
        with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name
        try:
            sbom = generate_sbom(tmp_path)
            project.sboms.append(SoftwareBillOfMaterials(content=json.dumps(sbom)))
        finally:
            os.remove(tmp_path)

    project.updated_at = datetime.utcnow()
    db.session.commit()

    if docker_composes:
        log_manager.add_log(log_level="info", user=current_user.name, function=update_project.__name__, argument=str(project.to_dict()), log_string="Docker compose files uploaded successfully")

    if dockerfiles:
        log_manager.add_log(log_level="info", user=current_user.name, function=update_project.__name__, argument=str(project.to_dict()), log_string="Dockerfiles uploaded successfully")

    if images:
        log_manager.add_log(log_level="info", user=current_user.name, function=update_project.__name__, argument=str(project.to_dict()), log_string="Docker images uploaded and SBOMs generated")

    log_manager.add_log(log_level="info", user=current_user.name, function=update_project.__name__, argument=str(project.to_dict()), log_string="Project updated successfully")
    return project.to_dict()
