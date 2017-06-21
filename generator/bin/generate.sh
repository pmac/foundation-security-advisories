#!/bin/bash

set -ex

cd generator
#python manage.py update_security_advisories
python manage.py generate_static_site
python manage.py collectstatic --noinput
