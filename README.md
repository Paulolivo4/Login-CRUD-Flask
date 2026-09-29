# Login-CRUD-Flask

Role-based restaurant web app built with **Flask** and **SQL Server**. Users sign in and are routed to a dashboard that depends on their role: **admins** register restaurants, **owners** manage menus, and **clients** manage reservations.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=flat-square&logo=render&logoColor=black)

## Features

- **Authentication:** login, logout, registration and a password-reset form.
- **Three roles**, each with its own blueprint and views:

  | Role (`ROL_ID`) | After login | Can do |
  | --- | --- | --- |
  | Admin (`1`) | `/users/dashboard` | Manage users; create and list restaurants (`/admin/restaurants`) |
  | Owner (`2`) | `/owner/menus` | Create, edit and delete menus |
  | Client (`3`, default) | `/client/reservations` | Create, update and delete reservations |

- **Route protection:** admin routes check the session role and return a custom `403` page for other roles; unauthenticated users are redirected to `/login`.
- **User CRUD** through `/users/` (create, update, delete).
- **MVC structure** with Flask blueprints. All database access goes through SQL Server **stored procedures** (`sp_ValidateLogin`, `sp_RegistrarUsuario`, `sp_CrearRestaurante`, `sp_CrearMenu`, `sp_CrearReserva`, and others).

## Tech stack

Python 3.11 · Flask · Jinja2 · pyodbc (ODBC Driver 17 for SQL Server) · Gunicorn (`procfile`) for deployment on Render.

## Project structure

```
app.py               # Flask app, blueprint registration, 403 handler
BDD/Conexion.py      # SQL Server connection (pyodbc)
CONTROLLER/          # Blueprints: login, user, admin, owner, client
MODEL/               # Data access via stored procedures
templates/VIEW/      # Jinja2 views (login, dashboards, menus, reservations)
procfile, runtime.txt
```

## Getting started

**Requirements:** Python 3.11+, a SQL Server instance reachable from your machine, and the [Microsoft ODBC Driver 17 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install Flask pyodbc gunicorn
python app.py
```

Then open <http://127.0.0.1:5000/>, which redirects to `/login`.

### Database

The connection string lives in `BDD/Conexion.py` (server, database `LOGINDB`, driver). Point it at your own SQL Server instance and create the database objects the models call: the tables and the stored procedures listed above. This repository does not include the SQL scripts.

Set `FLASK_DEBUG=1` to run in debug mode and `PORT` to change the port.

## Routes

| Route | Description |
| --- | --- |
| `/login`, `/register`, `/logout`, `/reset-password` | Authentication |
| `/users/`, `/users/dashboard` | User management (admin) |
| `/admin/restaurants` | Create and list restaurants (admin) |
| `/owner/menus` | Menu CRUD (owner) |
| `/client/reservations` | Reservation CRUD (client) |

## Roadmap

- [ ] Read the Flask `secret_key` and the database settings from environment variables
- [ ] Hash passwords and use a tokenized password-reset flow
- [ ] Add SQL scripts and a `requirements.txt`
- [ ] Automated tests

## Authors

- [@Paulolivo4](https://github.com/Paulolivo4)
- [@Isaaidk](https://github.com/Isaaidk)
