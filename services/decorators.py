from flask import redirect, url_for
from flask_login import current_user
from functools import wraps

from libs.logging_utils import log_manager

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            log_manager.add_log(log_level="warning", user=current_user.name, function=f.__name__, argument=str(args), log_string="User is not authenticated")
            return redirect(url_for('auth.login'))

        if not getattr(current_user, 'is_admin', False):
            log_manager.add_log(log_level="warning", user=current_user.name, function=f.__name__, argument=str(args), log_string="User is not admin")
            return redirect(url_for('home'))

        return f(*args, **kwargs)
    return decorated_function
