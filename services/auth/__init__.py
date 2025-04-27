from flask import Blueprint, request, flash, render_template, redirect, abort, url_for
from flask_login import login_user, login_required, logout_user

from .utils import url_has_allowed_host_and_scheme
from .password_utils import check
from services.sql.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user: User = User.query.filter_by(name=name).first()
        if user and check(password, user.password):
            login_user(user, remember=True)
            next = request.form.get('next', '/chat')
            if not url_has_allowed_host_and_scheme(next, request.host):
                return abort(400)
            return redirect(next)
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
