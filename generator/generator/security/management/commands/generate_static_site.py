import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.test import Client

from generator.security import models


KV_PAGE_PRODUCTS = (
    ('firefox', '3.6'),
    ('firefox', '3.5'),
    ('firefox', '3.0'),
    ('firefox', '2.0'),
    ('firefox', '1.5'),
    ('firefox', '1.0'),
    ('thunderbird', '3.1'),
    ('thunderbird', '3.0'),
    ('thunderbird', '2.0'),
    ('thunderbird', '1.5'),
    ('thunderbird', '1.0'),
    ('seamonkey', '2.0'),
    ('seamonkey', '1.1'),
    ('seamonkey', '1.0'),
)


def get_product_slug_urls():
    unique_slugs = set(p.product_slug for p in models.Product.objects.all())
    return ['/known-vulnerabilities/%s/' % s for s in unique_slugs]


class Command(BaseCommand):
    client = Client()

    def handle(self, *args, **options):
        output_path = settings.SITE_OUTPUT_PATH
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        all_urls = []
        all_urls.extend(settings.STATIC_PAGE_URLS)
        all_urls.extend([p.get_absolute_url() for p in models.Product.objects.all()])
        all_urls.extend([s.get_absolute_url() for s in models.SecurityAdvisory.objects.all()])
        all_urls.extend(get_product_slug_urls())
        for prod, vers in KV_PAGE_PRODUCTS:
            url = reverse('security.product-version-advisories',
                          kwargs={'product': prod, 'version': vers})
            if url not in all_urls:
                all_urls.append(url)

        count = 0
        for path in all_urls:
            resp = self.client.get(path)
            file_dir = os.path.join(output_path, path.lstrip('/'))
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

            file_path = os.path.join(file_dir, 'index.html')
            with open(file_path, 'wb') as fh:
                fh.write(resp.content)
                count += 1
                sys.stdout.write('.')
                sys.stdout.flush()

        print '\nOutput %d pages' % count

