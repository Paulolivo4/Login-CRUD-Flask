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

Python 3.11 · Flask · Jinja2 · pyodbc (ODBC Driver 17 for SQL Server) · Docker and Gunicorn for deployment on Render.

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
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:5000/>, which redirects to `/login`.

### Configuration

Settings are read from environment variables (see `.env.example`):

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session key. Set it in production; otherwise a random key is generated on each start | random |
| `DB_CONNECTION_STRING` | Full ODBC connection string; overrides the variables below | none |
| `DB_SERVER` | SQL Server host or instance | `localhost` |
| `DB_NAME` | Database name | `LOGINDB` |
| `DB_DRIVER` | ODBC driver | `ODBC Driver 17 for SQL Server` |
| `DB_USER`, `DB_PASSWORD` | SQL authentication; when unset, Windows authentication is used | none |
| `FLASK_DEBUG` | `1` enables debug mode | `0` |
| `PORT` | Port to listen on | `5000` |

Create the database objects the models call: the tables and the stored procedures listed above. This repository does not include the SQL scripts.

## Deploy on Render (Docker + Azure SQL)

Render's Python runtime does not include the Microsoft ODBC driver that `pyodbc` needs, so the app is deployed with the included `Dockerfile` (Python 3.11, ODBC Driver 18, Gunicorn).

1. Create a **Web Service** from this repository and choose **Docker** as the runtime (branch `main`).
2. Add these environment variables in Render:

   | Variable | Value |
   | --- | --- |
   | `SECRET_KEY` | A long random string |
   | `DB_CONNECTION_STRING` | `DRIVER={ODBC Driver 18 for SQL Server};SERVER=tcp:<server>.database.windows.net,1433;DATABASE=<db>;UID=<user>;PWD=<password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;` |

3. In the Azure portal, open the SQL server's **Networking** page and allow access from Render's outbound IP addresses (shown in the service's **Connect** menu).

To try the image locally:

```bash
docker build -t login-crud-flask .
docker run -p 8080:8080 -e PORT=8080 -e SECRET_KEY=dev login-crud-flask
```
## Routes

| Route | Description |
| --- | --- |
| `/login`, `/register`, `/logout`, `/reset-password` | Authentication |
| `/users/`, `/users/dashboard` | User management (admin) |
| `/admin/restaurants` | Create and list restaurants (admin) |
| `/owner/menus` | Menu CRUD (owner) |
| `/client/reservations` | Reservation CRUD (client) |

## Roadmap

- [ ] Hash passwords and use a tokenized password-reset flow
- [ ] Add SQL scripts for the tables and stored procedures
- [ ] Automated tests

## Authors

- [@Paulolivo4](https://github.com/Paulolivo4)
- [@Isaaidk](https://github.com/Isaaidk)
