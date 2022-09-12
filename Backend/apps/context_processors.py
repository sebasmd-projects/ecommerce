from django.conf import settings
import time


def custom_processors(request):
    ctx = {}
    ctx['base_url'] = settings.BASE_URL
    ctx['time'] = time.time()
    return ctx

"""
    Uso:
    <html>
        <body>
            {{ base_url }}
            {{ time }}
            {% if user.is_authenticated %}{{ user.username }}{% endif %}
        </body>
    </html>
"""