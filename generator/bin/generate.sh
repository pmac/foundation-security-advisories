#!/bin/bash

set -e

rm -rf _publish && mkdir _publish
cd generator
echo "Collecting static assets"
python manage.py collectstatic --noinput
echo "Updating security advisories"
python manage.py update_security_advisories
echo "Generating static HTML pages"
python manage.py generate_static_site
echo "Done"
