import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client

from generator.security import models


class Command(BaseCommand):
    client = Client()

    def handle(self, *args, **options):
        output_path = settings.SITE_OUTPUT_PATH
        print output_path
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        for path in settings.STATIC_PAGE_URLS:
            print path
            resp = self.client.get(path)
            file_dir = os.path.join(output_path, path.lstrip('/'))
            try:
                os.makedirs(file_dir)
            except os.error:
                pass

            file_path = os.path.join(file_dir, 'index.html')
            with open(file_path, 'wb') as fh:
                fh.write(resp.content)


