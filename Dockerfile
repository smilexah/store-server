## Use Alpine-based Python image
#FROM python:3.10-alpine
#
## Set environment variables
#ENV PYTHONUNBUFFERED=1 \
#    PYTHONDONTWRITEBYTECODE=1
#
## Set working directory
#WORKDIR /app
#
## Install Alpine build dependencies
#RUN apk add --no-cache \
#    gcc \
#    musl-dev \
#    libffi-dev \
#    postgresql-dev \
#    curl \
#    bash \
#    jpeg-dev \
#    zlib-dev \
#    libjpeg \
#    libjpeg-turbo-dev
#
## Install dockerize
#RUN curl -sSL https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz \
#    | tar -xz -C /usr/local/bin
#
## Copy and install dependencies
#COPY requirements.txt .
#RUN pip install --no-cache-dir --upgrade pip \
#    && pip install --no-cache-dir -r requirements.txt
#
## Copy application code
#COPY . .
#
## Expose port
#EXPOSE 8000
#
## Entrypoint command
##CMD ["sh", "-c", "dockerize -wait tcp://db:5432 -timeout 20s \
##    && python manage.py migrate \
##    && python manage.py collectstatic --noinput \
##    && python manage.py runserver 0.0.0.0:8000"]

# Stage 1: Base build stage
FROM python:3.10-slim AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies first for caching benefit
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.10-slim

RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Make entry file executable
RUN chmod +x  /app/entrypoint.prod.sh

# Start the application using Gunicorn
CMD ["/app/entrypoint.prod.sh"]