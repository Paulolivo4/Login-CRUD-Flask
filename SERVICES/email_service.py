import smtplib
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

class EmailService:
    # Credenciales centralizadas
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "isaacpuga661@gmail.com"
    SENDER_PASSWORD = "fxvj tbzy aoxr refw"

    @staticmethod
    def _send_email(destinatario, asunto, html_content):
        """Método privado interno para manejar el proceso de envío SMTP"""
        try:
            mensaje = MIMEText(html_content, "html", "utf-8")
            mensaje["Subject"] = asunto
            mensaje["From"] = EmailService.SENDER_EMAIL
            mensaje["To"] = destinatario

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as servidor:
                servidor.starttls()
                servidor.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                servidor.send_message(mensaje)
            
            logger.info(f"Correo enviado exitosamente a {destinatario}")
            return True
        except Exception as e:
            logger.error(f"Error crítico en el servidor SMTP: {e}")
            return False

    @staticmethod
    def send_password_reset(destinatario, nombre_usuario, codigo):
        """Envía el código de 6 dígitos para recuperar la cuenta"""
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #eee; border-radius: 10px; max-width: 500px; margin: auto;">
            <h2 style="color: #4f46e5; text-align: center;">Recuperación de Contraseña</h2>
            <hr>
            <p>Hola <strong>{nombre_usuario}</strong>,</p>
            <p>Has solicitado restablecer tu contraseña. Utiliza el siguiente código de seguridad para continuar con el proceso:</p>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <h1 style="color: #1f2937; letter-spacing: 10px; margin: 0; font-family: monospace;">{codigo}</h1>
            </div>
            <p style="font-size: 0.85rem; color: #666;">Este código expirará pronto. Si no solicitaste este cambio, puedes ignorar este correo de forma segura.</p>
            <hr>
            <p style="text-align: center; font-size: 0.75rem; color: #999;">Tasty App - Gestión de Reservas</p>
        </div>
        """
        return EmailService._send_email(destinatario, "Código de Recuperación de Contraseña", html)

    @staticmethod
    def send_payment_confirmation(destinatario, nombre_cliente, plato, total, fecha, metodo_pago):
        """Envía el comprobante de pago con el detalle de la reserva"""
        # Limpieza de fecha por si viene con formato 'T'
        fecha_limpia = fecha.replace('T', ' ') if 'T' in fecha else fecha

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border: 1px solid #ddd; padding: 20px; border-radius: 12px;">
                <h2 style="text-align: center; color: #2c3e50;">Confirmación de Reserva</h2>
                <p style="text-align: center; color: #27ae60; font-weight: bold;">¡Pago Realizado con Éxito!</p>
                <hr>
                <p>Hola <strong>{nombre_cliente}</strong>, gracias por tu compra. Aquí tienes los detalles de tu reserva:</p>

                <table width="100%" cellpadding="10" cellspacing="0" style="border-collapse: collapse; margin-top: 20px;">
                    <tr style="background-color: #f9fafb;">
                        <td style="border: 1px solid #eee;"><strong>Platillo</strong></td>
                        <td style="border: 1px solid #eee;">{plato}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #eee;"><strong>Fecha y Hora</strong></td>
                        <td style="border: 1px solid #eee;">{fecha_limpia}</td>
                    </tr>
                    <tr style="background-color: #f9fafb;">
                        <td style="border: 1px solid #eee;"><strong>Método de Pago</strong></td>
                        <td style="border: 1px solid #eee;">{metodo_pago}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #eee;"><strong>Total Cancelado</strong></td>
                        <td style="border: 1px solid #eee; color: #27ae60; font-weight: bold; font-size: 1.1rem;">${total}</td>
                    </tr>
                </table>

                <div style="margin-top: 30px; padding: 15px; background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;">
                    <p style="margin: 0; font-size: 0.9rem; color: #92400e; text-align: center;">
                        <strong>Nota:</strong> Presenta este comprobante digital al llegar al restaurante para validar tu reserva.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        asunto = f"Tu comprobante de reserva: {plato}"
        return EmailService._send_email(destinatario, asunto, html)