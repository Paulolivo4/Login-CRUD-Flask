from flask import Flask, render_template, request, redirect, url_for, session, flash
from MODEL import User 
from CONTROLLER.user_bp import user_bp  
from CONTROLLER.login_controller import login_bp
from CONTROLLER.client_controller import client_bp
from CONTROLLER.owner_controller import owner_bp
from CONTROLLER.admin_controller import admin_bp
import functools
import os

app = Flask(__name__)

app.secret_key = '12345678'
app.register_blueprint(user_bp)
app.register_blueprint(login_bp)
app.register_blueprint(client_bp)
app.register_blueprint(owner_bp)
app.register_blueprint(admin_bp)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_email' not in session:
            flash('Por favor, inicia sesión para acceder')
            return redirect(url_for('login_bp.login'))
        return view(**kwargs)
    return wrapped_view


@app.route('/')
def index():
    # Al abrir la aplicación, redirigir a la pantalla de login
    return redirect(url_for('login_bp.login'))


@app.errorhandler(403)
def forbidden(e):
    return render_template('VIEW/403.html'), 403

if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)
