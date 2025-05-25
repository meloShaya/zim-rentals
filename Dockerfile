# Pull official base Python Docker image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --upgrade pip

COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# Ensure entrypoint.sh is executable
RUN chmod +x /code/entrypoint.sh

# Expose the port (Render will use $PORT from environment)
EXPOSE 8000

# Run entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]

# Default CMD (will be overridden by Render's start command but good for local testing)
CMD ["daphne", "-p", "10000", "-b", "0.0.0.0", "zim_rentals.asgi:application"]
