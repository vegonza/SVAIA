from flask import redirect, url_for
from flask_login import current_user
from functools import wraps
from typing import Callable, Any
from typeguard import typechecked

from libs.logging_utils import log_manager


@typechecked
def admin_required(f: Callable) -> Callable:
    @wraps(f)
    @typechecked
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_authenticated:
            log_manager.add_log(log_level="warning", user=current_user.name, function=f.__name__, argument=str(args), log_string="User is not authenticated")
            return redirect(url_for('auth.login'))

        if not getattr(current_user, 'is_admin', False):
            log_manager.add_log(log_level="warning", user=current_user.name, function=f.__name__, argument=str(args), log_string="User is not admin")
            return redirect(url_for('home'))

        return f(*args, **kwargs)
    return decorated_function
