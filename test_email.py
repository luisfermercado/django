import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import django
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

try:
    send_mail(
        'Prueba desde Antigravity',
        'Este es un mensaje de prueba para verificar las credenciales SMTP de Google.',
        'info@cuanty.co',
        ['info@cuanty.co'],  # Enviar a sí mismo para probar
        fail_silently=False,
    )
    print("¡El correo se envió correctamente!")
except Exception as e:
    print(f"Error: {e}")
