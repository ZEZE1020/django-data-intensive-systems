#
# Dockerfile for django-data-intensive-systems
#
# This Dockerfile uses a multi-stage build to create a small, secure,
# and efficient image for production deployment.
#

# --- Builder Stage ---
# This stage installs Python dependencies into a virtual environment.
FROM python:3.13-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set up a virtual environment
RUN rm -rf /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install uv, the fast package installer
RUN pip install uv

# ARG to specify the requirements file to use
ARG REQUIREMENTS_FILE=requirements/prod.txt
ARG TEST_REQUIREMENTS_FILE=requirements/test.txt

# Copy requirements files
COPY requirements/ /app/requirements/

# Install dependencies into the virtual environment
RUN uv pip sync /app/${REQUIREMENTS_FILE}
RUN uv pip sync /app/${TEST_REQUIREMENTS_FILE}


# --- Final Stage ---
# This stage copies the application code and the virtual environment
# from the builder stage to create the final, lean image.
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
USER appuser

# Copy the virtual environment from the builder stage
COPY --chown=appuser:appuser --from=builder /opt/venv /opt/venv

# Copy the application code
COPY --chown=appuser:appuser . .

# Collect static files only in production
# The --no-input flag is important for non-interactive builds.
ARG REQUIREMENTS_FILE
RUN if [ "$REQUIREMENTS_FILE" = "requirements/prod.txt" ]; then python manage.py collectstatic --no-input; fi

# Expose the port Gunicorn will run on
EXPOSE 8000

# The command to run the application using Gunicorn
# This is a basic configuration; you might need to adjust the number of workers.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]