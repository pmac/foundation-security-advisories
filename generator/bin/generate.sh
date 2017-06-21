#!/bin/bash

set -ex

cd generator
python manage.py update_security_advisories
