import functools
from flask import session, redirect, url_for, abort, flash, request
from config import Config


def login_required(view):
   
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_email' not in session:
            flash('Por favor, inicia sesión para acceder')
            return redirect(url_for('login_bp.login', next=request.path))
        return view(**kwargs)
    return wrapped_view


def role_required(required_role):
    
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if 'user_email' not in session:
                flash('Por favor, inicia sesión para acceder')
                return redirect(url_for('login_bp.login', next=request.path))

            user_role = session.get('user_role')

            
            allowed_roles = required_role if isinstance(required_role, (list, tuple)) else [required_role]
            allowed_roles = [int(r) if isinstance(r, str) else r for r in allowed_roles]

            user_role = int(user_role) if isinstance(user_role, str) else user_role

            if user_role not in allowed_roles:
                flash('No autorizado para realizar esta acción')
                abort(403)

            return view(**kwargs)
        return wrapped_view
    return decorator
