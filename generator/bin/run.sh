#!/bin/bash

set -ex

cd generator
python manage.py runserver 0.0.0.0:8000
