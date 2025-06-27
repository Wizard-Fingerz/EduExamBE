from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from .models import ExaminationType
        def load_examination_types(sender, **kwargs):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            txt_path = os.path.join(base_dir, 'examination_types.txt')
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        name = line.strip()
                        if name:
                            ExaminationType.objects.get_or_create(name=name)
        post_migrate.connect(load_examination_types, sender=self)
