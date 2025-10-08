# LOGIN-FLASK

Proyecto Flask para login. Instrucciones rápidas para preparar el entorno virtual en Windows (PowerShell).

1) Crear el entorno virtual (si no está creado):

```powershell
python -m venv .venv
```

2) Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

3) Actualizar pip e instalar dependencias desde `requirements.txt`:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4) Ejecutar la aplicación:

```powershell
python app.py
```

# Login-CRUD-Flask 🚀🔐

<p align="center">
	<img alt="Login-CRUD-Flask" src="https://via.placeholder.com/900x180.png?text=Login-CRUD-Flask" width="900" />
</p>

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-3.x-orange.svg)](https://flask.palletsprojects.com/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

---

## Índice 📚

- [Descripción](#descripción)
- [Estado del proyecto](#estado-del-proyecto)
- [Características principales](#características-principales)
- [Tecnologías / Frameworks utilizados](#tecnologías--frameworks-utilizados)
- [Instalación (Windows - PowerShell)](#instalación-windows---powershell)
	- [Crear y activar entorno virtual](#crear-y-activar-entorno-virtual)
	- [Instalar dependencias](#instalar-dependencias)
	- [Ejecutar la app](#ejecutar-la-app)
- [Configuración de la base de datos](#configuración-de-la-base-de-datos-🔧)
- [Rutas principales / Uso](#rutas-principales--uso-🧭)
- [Recomendaciones de seguridad](#recomendaciones-de-seguridad-🔒)
- [Cómo contribuir](#cómo-contribuir-🤝)
- [Autores](#autores-👤)
- [Licencia](#licencia-📜)
- [FAQ y resolución de problemas](#faq-y-resolución-de-problemas-🛠️)

---

## Descripción

Proyecto de ejemplo en Flask que implementa autenticación básica (login/logout), registro de usuarios y operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre usuarios apoyándose en SQL Server a través de `pyodbc`. Es ideal como plantilla educativa y base para proyectos que necesiten un sistema de usuarios.

---

## Estado del proyecto

- ✅ Funcional para pruebas locales
- 🔧 En desarrollo: mejoras de seguridad (hash de contraseñas, tokens), tests automáticos y despliegue

---

## Características principales

- Login / Logout ✔️  
- Registro de usuarios ✔️  
- Listado de usuarios desde SQL Server ✔️  
- Crear / Actualizar / Eliminar usuarios (CRUD) ✔️  
- Restablecimiento de contraseña vía formulario público ✔️  
- Protección de rutas que requieren sesión (no accesibles por URL sin login) ✔️

---

## Tecnologías / Frameworks utilizados 🧩

- Python 3.11+ 🐍  
- Flask (web framework) ⚗️  
- Jinja2 (templates) 🧾  
- pyodbc (conector ODBC a SQL Server) 🗄️  
- ODBC Driver for SQL Server (Windows) — instalado en el sistema 🪟

---

## Instalación (Windows - PowerShell) ⚙️

Abre PowerShell en la carpeta del proyecto:

```powershell
Set-Location 'C:\Users\User\Desktop\Ingeniería web\LOGIN-FLASK'
```

### 1) Crear y activar entorno virtual

```powershell
# Crear entorno
python -m venv .venv

# Activar (PowerShell)
.\.venv\Scripts\Activate.ps1
```

> Si usas cmd.exe:
> ```
> .\.venv\Scripts\activate.bat
> ```

### 2) Actualizar pip e instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Si `requirements.txt` no existe o quieres instalar manualmente:
> ```powershell
> pip install Flask pyodbc
> ```

### 3) Ejecutar la aplicación

```powershell
python app.py
```

- Abre en el navegador: `http://127.0.0.1:5000/` (te redirige a `/login`).
- Para detener el servidor: presiona `Ctrl+C` en la terminal.

---

## Configuración de la base de datos 🔧

El proyecto incluye archivos en `BDD/` que leen `BDD/DatabaseConfig.txt`. Formato de ejemplo:

```
server=DESKTOP-XXXXXXX
database=LOGINDB
driver=ODBC Driver 17 for SQL Server
```

- Asegúrate de que SQL Server está accesible desde la máquina.
- Instala el driver ODBC de Microsoft (por ejemplo: ODBC Driver 17 for SQL Server). En Windows se descarga desde el sitio de Microsoft.
- Las consultas en el modelo (`MODEL/User.PY`) usan stored procedures (ej.: `sp_GetAllLoginDetails`, `sp_InsertLoginDetails`, `sp_UpdateLoginDetails`, `sp_DeleteLoginDetails`). Asegúrate que existan o adapta las consultas a tu esquema.

Recomendación: en vez de un archivo con credenciales, usa variables de entorno o `.env` (y `python-dotenv`) para mayor seguridad.

Ejemplo con variables de entorno (en `BDD/Conexion.py` leer `os.environ['DB_SERVER']`, etc.).

---

## Rutas principales / Uso 🧭

- `/` → Redirige a `/login`
- `/login` → Formulario de inicio de sesión
- `/login/submit` → Procesa inicio de sesión
- `/register` → Formulario de registro
- `/register/submit` → Crear nuevo usuario
- `/reset-password` → Formulario público para restablecer contraseña
- `/reset-password/submit` → Actualiza contraseña en DB
- `/users/` → Lista de usuarios (REQUIERE sesión)
- `/users/create`, `/users/update`, `/users/delete` → Operaciones CRUD (métodos POST)

> Nota: rutas del blueprint de usuarios (`/users/`) están protegidas; si intentas acceder sin sesión verás un 403 o serás redirigido al login según configuración.

---

## Recomendaciones de seguridad 🔒

- ¡NO subas credenciales al repositorio! Añade `BDD/DatabaseConfig.txt` a `.gitignore` si contiene secretos.
- Almacena contraseñas con hash (bcrypt). Actualmente la app puede comparar texto plano según la DB existente — actualizar a hashes es PRIORITARIO antes de producción.
- Usa HTTPS en producción.
- Protege rutas sensibles y valida todas las entradas del usuario (sanitización).
- Usa tokens (email token) para restablecer contraseñas en lugar de permitir cambios directos desde un formulario público.

---

## Cómo contribuir 🤝

1. Haz fork del repo en GitHub.  
2. Crea una rama: `git checkout -b feature/mi-cambio`.  
3. Haz commits atómicos y descriptivos.  
4. Abre un Pull Request describiendo los cambios.

Por favor, abre un issue antes de cambios grandes de arquitectura.

---

## Autores 👤

- Paulolivo4 — desarrollador principal

Si quieres añadir colaboradores, dímelo y lo agregamos al README.

---

## Licencia 📜

El proyecto no trae licencia por defecto. Si quieres compartirlo públicamente, te recomiendo MIT:

```
MIT License

Copyright (c) 2025 Paulolivo4

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

---

## FAQ y resolución de problemas 🛠️

Q: `pyodbc` falla al instalar o conectar  
A: Asegúrate de instalar el ODBC Driver de Microsoft para SQL Server (ej. Driver 17). Reinicia la máquina si es necesario.

Q: `git` no se reconoce en PowerShell  
A: Instala **Git for Windows** desde https://git-scm.com/download/win y reinicia PowerShell.

Q: Al acceder a `/users/` veo 403  
A: Estás intentando acceder sin inicio de sesión. Ve a `/login` o crea una cuenta en `/register`.

Q: ¿Cómo oculto mis credenciales antes de subir a GitHub?  
A: Añade `BDD/DatabaseConfig.txt` a `.gitignore` y mueve las credenciales a variables de entorno o a `.env` (no versionar `.env`).

---

Si quieres, puedo:

- Generar y añadir el `README.md` directamente al repo (si me lo confirmas).  
- Crear el `LICENSE` MIT y añadirlo.  
- Generar un `.env.example` con las variables necesarias.  
- Ayudarte a crear el repositorio en GitHub (te doy los pasos exactos o los ejecuto localmente si me autorizas).

¿Quieres que te entregue también una versión en inglés? 🌎
