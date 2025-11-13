from flask import redirect, url_for
from flask_login import current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.cargo != 'admin':
            return redirect(url_for('login'))  # ou página de acesso negado
        return f(*args, **kwargs)
    return decorated_function

def operador_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.cargo != 'operador':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
