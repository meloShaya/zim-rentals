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

# Run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
