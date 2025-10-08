from flask import Flask, render_template, request, redirect, url_for, session, flash
from MODEL import User  # Asegúrate que la carpeta MODEL tenga __init__.py
from CONTROLLER import user_controller  # Importa el controlador
from CONTROLLER.user_bp import user_bp  # Importa el Blueprint
from CONTROLLER.login_controller import login_bp
import functools

app = Flask(__name__)

app.secret_key = '12345678'
app.register_blueprint(user_bp)
app.register_blueprint(login_bp)


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

if __name__ == '__main__':
    app.run(debug=True)
