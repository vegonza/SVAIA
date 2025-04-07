from flask import Blueprint, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

class Usuario:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = { # Simulamos una base de datos de usuarios
    'user1': Usuario(id=1, username='user1', password=hash('pass1')),
    'user2': Usuario(id=2, username='user2', password=hash('pass2'))
}

def hash(password):
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def check(password, hash):
    return check_password_hash(hash, password)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check(password, user.password):
            login_user(user, remember=True)
            flash('Has iniciado sesión correctamente.', 'success')
            next = request.form.get('next', '/')
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
