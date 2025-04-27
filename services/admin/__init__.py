from flask import Blueprint, render_template
from flask_login import login_required

from services.decorators import admin_required

__all__ = ["admin_bp"]

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def index():
    return render_template("admin/admin.html")


@admin_bp.route("/user-projects/<int:user_id>")
@admin_required
def user_projects(user_id):
    return render_template("admin/projects.html", user_id=user_id)


@admin_bp.route("/project-messages/<string:project_uuid>")
@admin_required
def project_messages(project_uuid):
    return render_template("admin/project_messages.html", project_uuid=project_uuid)
