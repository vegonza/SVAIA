from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from .models import User, db
from services.auth.password_utils import hash

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
def list_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@users_bp.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('sql.users.create_user'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('El correo electrónico ya está en uso.', 'danger')
            return redirect(url_for('sql.users.create_user'))

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Usuario creado con éxito', 'success')
        return redirect(url_for('sql.users.list_users'))

    return render_template('user_form.html', user=None)


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')

        # Check if email is already in use by another user
        email_user = User.query.filter_by(email=email).first()
        if email_user and email_user.id != user.id:
            flash('El correo electrónico ya está en uso.', 'danger')
            return redirect(url_for('sql.users.edit_user', user_id=user_id))

        # Check if username is already in use by another user
        username_user = User.query.filter_by(username=username).first()
        if username_user and username_user.id != user.id:
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('sql.users.edit_user', user_id=user_id))

        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username

        # Update password if provided
        password = request.form.get('password')
        if password and password.strip():
            user.password = hash(password)

        db.session.commit()

        flash('Usuario actualizado con éxito', 'success')
        return redirect(url_for('sql.users.list_users'))

    return render_template('user_form.html', user=user)


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user: User = User.query.get_or_404(user_id)

    if False:  # user.id == current_user.id:  # TODO:
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('sql.users.list_users'))

    db.session.delete(user)
    db.session.commit()

    flash('Usuario eliminado con éxito', 'success')
    return redirect(url_for('sql.users.list_users'))
