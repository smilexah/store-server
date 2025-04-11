# Use Alpine-based Python image
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install Alpine build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    curl \
    bash \
    jpeg-dev \
    zlib-dev \
    libjpeg \
    libjpeg-turbo-dev

# Install dockerize
RUN curl -sSL https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
    | tar -xz -C /usr/local/bin

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Entrypoint command
#CMD ["sh", "-c", "dockerize -wait tcp://db:5432 -timeout 20s \
#    && python manage.py migrate \
#    && python manage.py collectstatic --noinput \
#    && python manage.py runserver 0.0.0.0:8000"]