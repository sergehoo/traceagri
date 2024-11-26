from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Définit le module de configuration Django pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traceagri.settings')

app = Celery("traceagri")

# Charge la configuration depuis Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Recherche automatiquement les tâches définies dans vos apps
app.autodiscover_tasks()
