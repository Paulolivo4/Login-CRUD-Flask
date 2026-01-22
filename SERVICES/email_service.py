import os
import requests
import logging

# Configuramos el logger para ver errores en la consola de Render
logger = logging.getLogger(__name__)

class EmailService:
    # URL oficial de la API de Brevo (v3)
    BREVO_URL = "https://api.brevo.com/v3/smtp/email"
    
    @staticmethod
    def _send_email(destinatario, asunto, html_content):
        """
        Envía un correo usando la API HTTPS de Brevo.
        Esto evita los bloqueos de puerto SMTP (465/587) de Render.
        """
        # Obtenemos las credenciales de las variables de entorno de Render
        api_key = os.environ.get('BREVO_API_KEY')
        sender_email = os.environ.get('EMAIL_USER')
        
        # Validaciones de seguridad
        if not api_key:
            logger.error("❌ ERROR CRÍTICO: No se encontró 'BREVO_API_KEY' en las variables de entorno.")
            return False
        if not sender_email:
            logger.error("❌ ERROR CRÍTICO: No se encontró 'EMAIL_USER' en las variables de entorno.")
            return False

        # Construcción del mensaje para la API de Brevo
        payload = {
            "sender": {
                "name": "Soporte UFood",  # Puedes cambiar este nombre
                "email": sender_email     # Debe coincidir con el correo de tu cuenta Brevo
            },
            "to": [
                {
                    "email": destinatario
                }
            ],
            "subject": asunto,
            "htmlContent": html_content
        }
        
        # Cabeceras obligatorias
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }

        try:
            # Enviamos la petición POST (Puerto 443, seguro y sin bloqueos)
            response = requests.post(EmailService.BREVO_URL, json=payload, headers=headers)
            
            # Brevo devuelve 201 Created si todo salió bien
            if response.status_code == 201 or response.status_code == 200:
                logger.info(f"✅ Correo enviado exitosamente a {destinatario}")
                return True
            else:
                # Si falla, mostramos el mensaje exacto de Brevo
                logger.error(f"❌ Brevo rechazó el envío: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error de conexión con Brevo: {str(e)}")
            return False

    @staticmethod
    def send_password_reset(destinatario, nombre_usuario, codigo):
        """Plantilla HTML para recuperar contraseña"""
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
            <h2 style="color: #4f46e5; text-align: center;">Recuperación de Contraseña</h2>
            <p style="color: #333;">Hola <strong>{nombre_usuario}</strong>,</p>
            <p style="color: #555;">Hemos recibido una solicitud para restablecer tu contraseña. Utiliza el siguiente código de seguridad:</p>
            
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; margin: 25px 0;">
                <span style="font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #1f2937;">{codigo}</span>
            </div>
            
            <p style="color: #999; font-size: 12px; text-align: center;">Si no solicitaste este cambio, por favor ignora este mensaje.</p>
        </div>
        """
        return EmailService._send_email(destinatario, "Código de Recuperación - UFood", html)

    @staticmethod
    def send_payment_confirmation(destinatario, nombre_cliente, plato, total, fecha, metodo_pago):
        """Plantilla HTML para confirmación de pago"""
        # Limpiamos la fecha si viene con formato ISO
        fecha_display = fecha.replace('T', ' ') if 'T' in fecha else fecha
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #10b981; text-align: center;">¡Reserva Confirmada!</h2>
            <hr style="border: 0; border-top: 1px solid #eee;">
            <p>Hola <strong>{nombre_cliente}</strong>,</p>
            <p>Tu pago ha sido procesado exitosamente. Aquí están los detalles de tu reserva:</p>
            
            <table width="100%" style="border-collapse: collapse; margin-top: 15px;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Plato:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{plato}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Fecha:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{fecha_display}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Total Pagado:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-size: 18px; color: #10b981;"><strong>${total}</strong></td>
                </tr>
            </table>
            
            <p style="margin-top: 30px; text-align: center; color: #666;">¡Te esperamos!</p>
        </div>
        """
        asunto = f"Reserva Confirmada: {plato}"
        return EmailService._send_email(destinatario, asunto, html)