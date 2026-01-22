import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os

logger = logging.getLogger(__name__)

class EmailService:
    # Credenciales desde variables de entorno
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465  # <--- CAMBIO IMPORTANTE: Puerto SSL directo
    SENDER_EMAIL = os.environ.get('EMAIL_USER')
    SENDER_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    @staticmethod
    def _send_email(destinatario, asunto, html_content):
        """Método privado interno para manejar el proceso de envío SMTP"""
        try:
            # Validar que tenemos credenciales
            if not EmailService.SENDER_EMAIL or not EmailService.SENDER_PASSWORD:
                logger.error("Credenciales de email no configuradas en Render")
                return False
            
            # Crear el mensaje
            mensaje = MIMEMultipart()
            mensaje["Subject"] = asunto
            mensaje["From"] = EmailService.SENDER_EMAIL
            mensaje["To"] = destinatario
            mensaje.attach(MIMEText(html_content, "html", "utf-8"))

            # <--- CAMBIO CRÍTICO AQUÍ: Usamos SMTP_SSL --->
            # timeout=20 evita que se quede colgado eternamente
            with smtplib.SMTP_SSL(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=20) as servidor:
                servidor.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                servidor.send_message(mensaje)
            
            logger.info(f"✅ Correo enviado exitosamente a {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error crítico enviando correo: {str(e)}")
            return False

    @staticmethod
    def send_password_reset(destinatario, nombre_usuario, codigo):
        """Envía el código de 6 dígitos para recuperar la cuenta"""
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #eee; border-radius: 10px; max-width: 500px; margin: auto;">
            <h2 style="color: #4f46e5; text-align: center;">Recuperación de Contraseña</h2>
            <hr>
            <p>Hola <strong>{nombre_usuario}</strong>,</p>
            <p>Has solicitado restablecer tu contraseña. Utiliza el siguiente código de seguridad:</p>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h1 style="color: #1f2937; letter-spacing: 10px; margin: 0; font-family: monospace;">{codigo}</h1>
            </div>
            <p style="font-size: 0.85rem; color: #666;">Si no solicitaste este cambio, ignora este correo.</p>
        </div>
        """
        return EmailService._send_email(destinatario, "Código de Recuperación de Contraseña", html)

    @staticmethod
    def send_payment_confirmation(destinatario, nombre_cliente, plato, total, fecha, metodo_pago):
        """Envía el comprobante de pago con el detalle de la reserva"""
        fecha_limpia = fecha.replace('T', ' ') if 'T' in fecha else fecha

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border: 1px solid #ddd; padding: 20px; border-radius: 12px;">
                <h2 style="text-align: center; color: #2c3e50;">Confirmación de Reserva</h2>
                <p style="text-align: center; color: #27ae60; font-weight: bold;">¡Pago Realizado con Éxito!</p>
                <hr>
                <p>Hola <strong>{nombre_cliente}</strong>, aquí tienes los detalles de tu reserva:</p>
                <table width="100%" cellpadding="10" cellspacing="0" style="border-collapse: collapse; margin-top: 20px;">
                    <tr>
                        <td style="border: 1px solid #eee;"><strong>Platillo</strong></td>
                        <td style="border: 1px solid #eee;">{plato}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #eee;"><strong>Total</strong></td>
                        <td style="border: 1px solid #eee; color: #27ae60; font-weight: bold;">${total}</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        asunto = f"Tu comprobante de reserva: {plato}"
        return EmailService._send_email(destinatario, asunto, html)