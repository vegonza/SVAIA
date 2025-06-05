from flask import Blueprint, request, flash, render_template, redirect, abort, url_for
from flask_login import login_user, login_required, logout_user, current_user

from .utils import url_has_allowed_host_and_scheme
from .password_utils import check
from services.sql.models import User
from libs.logging_utils import log_manager
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user: User = User.query.filter_by(name=name).first()
        if user and check(password, user.password):
            login_user(user, remember=True)
            next = request.form.get('next', '/chat')
            if not url_has_allowed_host_and_scheme(next, request.host):
                log_manager.add_log(log_level="warning", user=user.name, function=login.__name__, argument=str(request.form), log_string="Invalid next URL")
                return abort(400)
            log_manager.add_log(log_level="info", user=user.name, function=login.__name__, argument=str(request.form), log_string="Login successful")
            return redirect(next)
        else:
            log_manager.add_log(log_level="warning", user=user.name, function=login.__name__, argument=str(request.form), log_string="Invalid credentials")
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_manager.add_log(log_level="info", user=current_user.name, function=logout.__name__, argument="", log_string="Logout")
    logout_user()
    return redirect(url_for('home'))
