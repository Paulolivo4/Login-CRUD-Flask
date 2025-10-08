# from flask import Flask, render_template, request, redirect, url_for, session
# import pyodbc
# from MODEL import User 

# app = Flask(__name__)

# @app.route('/')
# def index():
#     usuarios = User.obtenerusuarios()
#     return render_template('index.html', usuarios=usuarios)

# @app.route('/create', methods=[ 'POST'])
# def create_user():
#     name = request.form['name']
#     lastname = request.form['lastname']
#     email = request.form['email']
#     password = request.form['password']
#     User.create_new_USER(name, lastname, email, password)
#     return ("Ingreso esitoso" +redirect(url_for('index')))

# @app.route('/update', methods=[ 'POST'])
# def update_user():
#     email = request.form['email']
#     new_password = request.form['new_password']
#     User.update_user(email, new_password)
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)
    