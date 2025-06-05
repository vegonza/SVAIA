from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from typing import Any

from libs.logging_utils import log_manager
from services.auth.password_utils import hash
from services.decorators import admin_required

from .models import User, db

users_bp = Blueprint('users', __name__)


@users_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('sql.users.create_user'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('El correo electrónico ya está en uso.', 'danger')
            return redirect(url_for('sql.users.create_user'))

        new_user = User(
            name=name,
            last_name=last_name,
            email=email,
            password=hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Usuario creado con éxito', 'success')
        log_manager.add_log(log_level="info", user=current_user.name, function=create_user.__name__, argument=str(new_user.to_dict()), log_string="User created successfully")
        return redirect(url_for('admin.index'))

    return render_template('user_form.html', user=None)


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id: int):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        # Check if email is already in use by another user
        email_user = User.query.filter_by(email=email).first()
        if email_user and email_user.id != user.id:
            flash('El correo electrónico ya está en uso.', 'danger')
            return redirect(url_for('sql.users.edit_user', user_id=user_id))

        # Check if name is already in use by another user
        name_user = User.query.filter_by(name=name).first()
        if name_user and name_user.id != user.id:
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('sql.users.edit_user', user_id=user_id))

        # Update user
        user.name = name
        user.last_name = last_name
        user.email = email

        # Update password if provided
        password = request.form.get('password')
        if password and password.strip():
            user.password = hash(password)

        db.session.commit()

        flash('Usuario actualizado con éxito', 'success')
        return redirect(url_for('admin.index'))

    log_manager.add_log(log_level="info", user=current_user.name, function=edit_user.__name__, argument=str(user.to_dict()), log_string="User updated successfully")
    return render_template('user_form.html', user=user)


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id: int):
    user: User = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('admin.index'))

    db.session.delete(user)
    db.session.commit()

    flash('Usuario eliminado con éxito', 'success')
    log_manager.add_log(log_level="info", user=current_user.name, function=delete_user.__name__, argument=str(user.to_dict()), log_string="User deleted successfully")
    return redirect(url_for('admin.index'))


@users_bp.route('/all', methods=['GET'])
@admin_required
def get_all_users() -> list[dict[str, Any]]:
    users = User.query.all()
    return [user.to_dict() for user in users]
