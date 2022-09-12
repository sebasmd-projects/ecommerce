import json
from django.core.exceptions import ImproperlyConfigured

with open('settings.json') as f:
    valor = json.loads(f.read())
    
def obtener_valor(titulo, valores = valor):
    try:
        return valores[titulo]
    except:
        msg = f'No se encontró el valor {titulo}'
        raise ImproperlyConfigured(msg)
    
    
