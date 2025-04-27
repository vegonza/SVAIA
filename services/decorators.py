from flask import redirect, url_for
from flask_login import current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        if not getattr(current_user, 'is_admin', False):
            return redirect(url_for('home'))

        return f(*args, **kwargs)
    return decorated_function
