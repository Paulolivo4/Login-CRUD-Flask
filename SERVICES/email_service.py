import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    # CONFIGURACIÓN BLINDADA PARA RENDER
    # Usamos Puerto 465 y SSL directo para evitar Timeouts
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    
    # Obtenemos las variables SIN valores por defecto para evitar errores silenciosos
    SENDER_EMAIL = os.environ.get('EMAIL_USER')
    SENDER_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    @staticmethod
    def _send_email(destinatario, asunto, html_content):
        """Método privado interno para manejar el proceso de envío SMTP SSL"""
        try:
            # 1. Validación temprana de credenciales
            if not EmailService.SENDER_EMAIL or not EmailService.SENDER_PASSWORD:
                logger.error("❌ ERROR CRÍTICO: Faltan las variables de entorno EMAIL_USER o EMAIL_PASSWORD en Render.")
                return False
            
            # 2. Crear el mensaje
            mensaje = MIMEMultipart()
            mensaje["Subject"] = asunto
            mensaje["From"] = EmailService.SENDER_EMAIL
            mensaje["To"] = destinatario
            mensaje.attach(MIMEText(html_content, "html", "utf-8"))

            # 3. Conexión Segura (SSL) - Esto evita el bloqueo del puerto 587
            # El timeout=20 asegura que si falla, te avise rápido y no congele la app
            logger.info(f"Intentando conectar a Gmail por puerto {EmailService.SMTP_PORT}...")
            
            with smtplib.SMTP_SSL(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=20) as servidor:
                servidor.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                servidor.send_message(mensaje)
            
            logger.info(f"✅ Correo enviado exitosamente a {destinatario}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ ERROR DE AUTENTICACIÓN: Tu correo o contraseña son incorrectos. Revisa que NO tengan espacios en Render.")
            return False
        except Exception as e:
            logger.error(f"❌ Error enviando correo: {str(e)}")
            return False

    @staticmethod
    def send_password_reset(destinatario, nombre_usuario, codigo):
        """Envía el código de 6 dígitos para recuperar la cuenta"""
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #eee; border-radius: 10px; max-width: 500px; margin: auto;">
            <h2 style="color: #4f46e5; text-align: center;">Recuperación de Contraseña</h2>
            <hr>
            <p>Hola <strong>{nombre_usuario}</strong>,</p>
            <p>Has solicitado restablecer tu contraseña. Tu código es:</p>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h1 style="color: #1f2937; letter-spacing: 10px; margin: 0; font-family: monospace;">{codigo}</h1>
            </div>
            <p style="font-size: 0.85rem; color: #666;">Si no fuiste tú, ignora este mensaje.</p>
        </div>
        """
        return EmailService._send_email(destinatario, "Restablecer Contraseña - Tasty App", html)

    @staticmethod
    def send_payment_confirmation(destinatario, nombre_cliente, plato, total, fecha, metodo_pago):
        """Envía el comprobante de pago"""
        fecha_limpia = fecha.replace('T', ' ') if 'T' in fecha else fecha

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; border-radius: 12px; max-width: 600px; margin: auto;">
            <h2 style="text-align: center; color: #2c3e50;">¡Reserva Confirmada!</h2>
            <p>Hola <strong>{nombre_cliente}</strong>, aquí tienes tu comprobante:</p>
            <table width="100%" cellpadding="10" cellspacing="0" style="border-collapse: collapse;">
                <tr><td style="border-bottom:1px solid #eee;"><strong>Plato:</strong></td><td style="border-bottom:1px solid #eee;">{plato}</td></tr>
                <tr><td style="border-bottom:1px solid #eee;"><strong>Total:</strong></td><td style="border-bottom:1px solid #eee; color: green; font-weight: bold;">${total}</td></tr>
            </table>
        </div>
        """
        return EmailService._send_email(destinatario, f"Reserva Confirmada: {plato}", html)