import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    # VOLVEMOS AL PUERTO 587 (El 465 está bloqueado en tu red)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    SENDER_EMAIL = os.environ.get('EMAIL_USER')
    SENDER_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    @staticmethod
    def _send_email(destinatario, asunto, html_content):
        try:
            # 1. Validación
            if not EmailService.SENDER_EMAIL or not EmailService.SENDER_PASSWORD:
                logger.error("❌ ERROR: Faltan credenciales EMAIL_USER o EMAIL_PASSWORD")
                return False
            
            # 2. Preparar mensaje
            mensaje = MIMEMultipart()
            mensaje["Subject"] = asunto
            mensaje["From"] = EmailService.SENDER_EMAIL
            mensaje["To"] = destinatario
            mensaje.attach(MIMEText(html_content, "html", "utf-8"))

            # 3. Conexión Standard con Timeout explícito
            logger.info(f"Conectando a {EmailService.SMTP_SERVER}:{EmailService.SMTP_PORT}...")
            
            # Usamos SMTP normal (no SSL) porque el puerto 587 requiere upgrade con starttls
            server = smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=30)
            
            # Activar modo depuración para ver detalles en los logs de Render
            server.set_debuglevel(1) 
            
            server.ehlo()        # Saludo 1
            server.starttls()    # Encriptar la conexión
            server.ehlo()        # Saludo 2 (ya encriptado)
            
            # Login y Envío
            server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
            server.send_message(mensaje)
            server.quit()
            
            logger.info(f"✅ Correo enviado a {destinatario}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ ERROR DE AUTENTICACIÓN: Revisa tu contraseña en Render (asegúrate que no tenga espacios).")
            return False
        except Exception as e:
            logger.error(f"❌ Error enviando correo: {str(e)}")
            return False

    @staticmethod
    def send_password_reset(destinatario, nombre_usuario, codigo):
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; max-width: 500px; margin: auto;">
            <h2 style="color: #4f46e5; text-align: center;">Tu código de seguridad</h2>
            <div style="background-color: #f3f4f6; padding: 15px; text-align: center; margin: 20px 0;">
                <h1 style="color: #333; letter-spacing: 5px; margin: 0;">{codigo}</h1>
            </div>
            <p>Hola {nombre_usuario}, usa este código para restablecer tu contraseña.</p>
        </div>
        """
        return EmailService._send_email(destinatario, "Restablecer Contraseña", html)

    @staticmethod
    def send_payment_confirmation(destinatario, nombre_cliente, plato, total, fecha, metodo_pago):
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Reserva Confirmada</h2>
            <p>Cliente: {nombre_cliente}</p>
            <p>Plato: {plato}</p>
            <p>Total: <strong>${total}</strong></p>
        </div>
        """
        return EmailService._send_email(destinatario, f"Reserva Confirmada: {plato}", html)