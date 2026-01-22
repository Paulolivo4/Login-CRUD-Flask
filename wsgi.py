import os
import sys
import traceback

print("[WSGI] Iniciando aplicación Flask...")
print(f"[WSGI] Python version: {sys.version}")
print(f"[WSGI] Path: {sys.path}")

try:
    from app import create_app
    print("[WSGI] ✓ Módulo app importado correctamente")
    
    app = create_app()
    print("[WSGI] ✓ Aplicación Flask creada exitosamente")
    
except Exception as e:
    print(f"[WSGI] ❌ ERROR CRÍTICO al inicializar app: {e}")
    traceback.print_exc()
    
    # Crear una app dummy para que Render no falle completamente
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'error', 'message': f'App failed to initialize: {str(e)}'}), 500
    
    print("[WSGI] Dummy app creada para debugging")
