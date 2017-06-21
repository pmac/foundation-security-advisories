FROM python:2.7-slim

WORKDIR /app
CMD ["generator/bin/generate.sh"]

# Set Python-related environment variables to reduce annoying-ness
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV LANG=C.UTF-8
ENV DJANGO_SETTINGS_MODULE=generator.settings

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
