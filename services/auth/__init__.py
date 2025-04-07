from flask import Blueprint, request, flash, render_template
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .test_users import users

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def check(password, hash):
    return check_password_hash(hash, password)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)
        if user and check(password, user.password):
            login_user(user, remember=True)
            flash('Has iniciado sesión correctamente.', 'success')
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
    flash('Has cerrado la sesión.', 'info')
    return redirect(url_for('login'))
