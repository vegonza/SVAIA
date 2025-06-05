from services.sql.models import Project
from typeguard import typechecked

from .types import File


@typechecked
def collect_project_files(project: Project) -> list[File]:
    files = []

    # Add dockerfiles
    for dockerfile in project.dockerfiles:
        files.append(File(
            name=f"dockerfile_{dockerfile.id}",
            content=dockerfile.content
        ))

    # Add docker-compose files
    for docker_compose in project.docker_composes:
        files.append(File(
            name="docker-compose.yml",
            content=docker_compose.content
        ))

    # Add SBOMs
    for sbom in project.sboms:
        files.append(File(
            name=f"sbom_{sbom.id}.json",
            content=sbom.content
        ))

    return files


@typechecked
def get_project_criteria(project: Project) -> dict:
    return {
        "solvability_criteria": project.solvability_criteria,
        "max_vulnerability_level": project.max_vulnerability_level,
        "total_vulnerabilities_criteria": project.total_vulnerabilities_criteria
    }
