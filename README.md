# Zim Rentals

A house rental platform for Zimbabweans, connecting landlords and renters in major cities across Zimbabwe.

## Features

### For Landlords

-   Sign up and login with email/phone number
-   List rental properties with detailed information
-   Upload property photos
-   Manage listings
-   Receive direct inquiries from potential renters

### For Renters

-   Search and filter rental listings
-   View detailed property information
-   Contact landlords directly
-   Save favorite listings
-   Get location directions
-   Set up price alerts for new listings matching specific criteria

### Admin Features

-   Moderate listings
-   Verify landlord accounts
-   Manage user reports
-   View analytics

## Setup and Running the Application

This project is configured to run using Docker (recommended) or locally for development.

### A. Dockerized Environment (Recommended)

This is the recommended way to run the application for both development and a production-like setup.

**Prerequisites:**

-   Docker: [Install Docker](https://docs.docker.com/get-docker/)
-   Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

**Environment Variables:**

-   The `docker-compose.yml` file sets default credentials for the PostgreSQL database (`postgres` user, `postgres` password) and configures `DJANGO_SETTINGS_MODULE=zim_rentals.settings.prod` for the `web` (uWSGI) and `daphne` services.
-   For sensitive information or customizations (e.g., `SECRET_KEY`, `GOOGLE_MAPS_API_KEY`, or a production `DATABASE_URL` for Render), create a `.env` file in the project root. Copy `.env.example` to `.env` and fill in your values. Docker Compose will automatically load variables from this file.
    ```bash
    cp .env.example .env
    ```
    **Important**: The `.env` file should NOT be committed to version control.

**Building and Running:**

1.  **Build Images (if needed):**
    If you've changed `Dockerfile` or want to ensure fresh images:

    ```bash
    docker compose build
    ```

2.  **Start Services:**
    To start all services (database, cache, web, nginx, daphne) in detached mode:
    ```bash
    docker compose up -d
    ```

**Initial Setup (First Run):**

-   The `entrypoint.sh` script within the `web` container automatically waits for the database, applies database migrations (`python manage.py migrate`), and collects static files (`python manage.py collectstatic --noinput --clear`).
-   To **create a superuser**:
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```
    Follow the prompts to set up your admin account.

**Accessing the Application:**

-   Main application (via Nginx): `http://localhost:8080`
-   Django Admin: `http://localhost:8080/admin/`

**Stopping the Application:**

```bash
docker compose down
```

To remove volumes (database data, etc.): `docker compose down -v`

**Viewing Logs:**

```bash
docker compose logs <service_name>
# Examples:
# docker compose logs web
# docker compose logs nginx
# docker compose logs -f web  # Follow logs
```

### B. Local Development Environment (Without Docker)

This setup is for developers who prefer to manage services like Python, PostgreSQL, and Redis directly on their machine.

**Prerequisites:**

-   Python 3.10
-   PostgreSQL (running and configured)
-   Redis (running and configured)
-   A way to set environment variables (e.g., direnv, or manually exporting them)

**Setup Steps:**

1.  **Create a virtual environment:**

    ```bash
    python3.10 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**

    -   Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    -   Edit the `.env` file. **Crucially, for local development, set:**
        ```
        DJANGO_SETTINGS_MODULE=zim_rentals.settings.local
        ```
    -   Configure your `DATABASE_URL` (e.g., `DATABASE_URL=postgres://youruser:yourpassword@localhost:5432/yourdbname`).
    -   Ensure `SECRET_KEY`, `GOOGLE_MAPS_API_KEY`, and `REDIS_URL` (e.g., `REDIS_URL=redis://localhost:6379/0`) are set.
    -   Load these variables into your shell (e.g., `export $(cat .env | xargs)` or use a tool like `direnv`).

4.  **Database Setup:**

    -   Ensure your PostgreSQL server is running and you have created the database specified in `DATABASE_URL`.
    -   Run migrations (ensure `DJANGO_SETTINGS_MODULE` is set in your environment):
        ```bash
        python manage.py migrate
        ```

5.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**

    -   For the standard Django development server (HTTP only):
        ```bash
        python manage.py runserver
        ```
        (Access at `http://localhost:8000` or the port shown)
    -   For Daphne (to support WebSockets for chat/notifications):
        ```bash
        daphne -p 8000 zim_rentals.asgi:application
        ```
        (Access at `http://localhost:8000`)

7.  **Run Celery (for background tasks like price alerts):**
    _(Ensure Redis is running and `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` point to it, typically configured in `settings/local.py` to use `REDIS_URL`)_
    -   Start Celery worker:
        ```bash
        celery -A zim_rentals worker -l info
        ```
    -   Start Celery beat (for scheduled tasks):
        ```bash
        celery -A zim_rentals beat -l info
        ```

## Settings Management

The project uses a split settings structure located in the `zim_rentals/settings/` directory:

-   `base.py`: Contains common settings inherited by other files.
-   `local.py`: Settings specifically for local development (e.g., `DEBUG = True`, local database, often uses SQLite by default if `DATABASE_URL` isn't set for Postgres, simpler static file handling).
-   `prod.py`: Settings for production and Dockerized environments (e.g., `DEBUG = False`, PostgreSQL, Redis, configured for robust static file serving with WhiteNoise, security settings).

The active settings file is determined by the `DJANGO_SETTINGS_MODULE` environment variable.

## Price Alerts Setup

The Price Alerts feature allows users to:

-   Save search criteria for properties
-   Receive email notifications when new matching listings are posted
-   Receive real-time in-app notifications via WebSockets
-   View all their saved searches

This feature requires:

-   Redis for WebSocket communication (via Django Channels) and as a Celery broker.
-   Celery for background task processing and scheduled checks.
    (These are automatically set up in the Docker environment).

## API Documentation

Zim Rentals provides a RESTful API for integrating with other applications or building custom clients.

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1.  Obtain a token (example using HTTPie or curl):

    ```bash
    # HTTPie
    # http POST http://localhost:8080/api/token/ username="your_username" password="your_password"

    # curl
    curl -X POST http://localhost:8080/api/token/ \
      -H "Content-Type: application/json" \
      -d '{"username": "your_username", "password": "your_password"}'
    ```

2.  Use the `access` token from the response in subsequent requests via the `Authorization` header:

    ```bash
    # HTTPie
    # http GET http://localhost:8080/api/listings/ "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

    # curl
    curl -X GET http://localhost:8080/api/listings/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
    ```

3.  Refresh token (when the access token expires):
    ```bash
    # curl
    curl -X POST http://localhost:8080/api/token/refresh/ \
      -H "Content-Type: application/json" \
      -d '{"refresh": "YOUR_REFRESH_TOKEN_FROM_STEP_1"}'
    ```

### Endpoints

_(Note: Base URL is `http://localhost:8080/api/` when running with Docker, or the relevant port for local setup)._

#### Listings

-   `GET /listings/` - List all listings
-   `POST /listings/` - Create a new listing (requires authentication)
-   `GET /listings/{id}/` - Get details for a specific listing
-   `PUT /listings/{id}/` - Update a listing (owner only)
-   `DELETE /listings/{id}/` - Delete a listing (owner only)
-   `POST /listings/{id}/favorite/` - Favorite a listing
-   `POST /listings/{id}/unfavorite/` - Unfavorite a listing
-   `GET /listings/favorites/` - Get user's favorited listings

#### Listing Images

-   `GET /listing-images/` - List all images
-   `POST /listing-images/` - Upload a new image (for listing owner)
-   `GET /listing-images/{id}/` - Get a specific image
-   `DELETE /listing-images/{id}/` - Delete an image (owner only)

#### Favorites

-   `GET /favorites/` - List user's favorites
-   `POST /favorites/` - Create a new favorite
-   `DELETE /favorites/{id}/` - Remove a favorite

#### Chat Messages

-   `GET /listings/{id}/messages/` - Get all messages for a listing
-   `POST /listings/{id}/messages/` - Send a message for a listing
-   `GET /listings/{id}/messages/{message_id}/` - Get a specific message
-   `POST /listings/{id}/messages/{message_id}/mark_read/` - Mark a message as read

_(Other endpoints might exist, refer to `urls.py` and DRF router configurations for a complete list)._

### Examples

#### Creating a listing (example using curl):

```bash
curl -X POST http://localhost:8080/api/listings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cozy apartment in Harare",
    "description": "Beautiful 2-bedroom apartment",
    "price": "150.00",
    "currency": "USD",
    "city": "harare",
    "suburb": "Avondale",
    "address": "15 Example Street",
    "property_type": "apartment",
    "bedrooms": 2,
    "bathrooms": 1,
    "is_furnished": true,
    "has_water": true,
    "has_electricity": true,
    "has_wifi": false,
    "phone_number": "+263771234567"
  }'
```

## Deployment

This application is configured for deployment on platforms like [Render](https://render.com/).

-   It uses `zim_rentals.settings.prod` for production builds.
-   Configuration heavily relies on environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`, `DJANGO_SETTINGS_MODULE`).
-   The build process on such platforms should typically include:
    ```bash
    pip install -r requirements.txt
    python manage.py collectstatic --noinput --clear
    python manage.py migrate
    ```
-   The start command for the web service would be Gunicorn (for WSGI) or Daphne (for ASGI, if Render supports it directly for the main web service). For example:

    ```bash
    # For Gunicorn (WSGI)
    gunicorn zim_rentals.wsgi:application --bind 0.0.0.0:$PORT

    # Or for Daphne (ASGI), if separate from web workers:
    # daphne -b 0.0.0.0 -p $PORT zim_rentals.asgi:application
    ```

    (Render typically injects a `$PORT` environment variable).

## Technologies Used

-   Python
-   Django
-   Django REST framework
-   Django Channels (for WebSockets)
-   Daphne (ASGI server)
-   UWSGI / Gunicorn (WSGI server)
-   PostgreSQL
-   Redis (for caching and Channels layer)
-   Celery (for background tasks)
-   Docker & Docker Compose
-   Nginx (as a reverse proxy in Docker setup)
-   Bootstrap 5
-   Django Allauth (for authentication)
-   Django Crispy Forms (for form rendering)
-   Django Geoposition (for location services)
-   WhiteNoise (for serving static files in production)
