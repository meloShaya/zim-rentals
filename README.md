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

## Setup Instructions

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env.example` file in the project root (if it doesn't exist) with the necessary environment variables documented.
   Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then, edit the `.env` file and fill in your actual secret values (e.g., `SECRET_KEY`, `DB_PASSWORD`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `GOOGLE_MAPS_API_KEY`).
**Important**: The `.env` file should NOT be committed to version control.

4. Run migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Run the development server with one of the following:

```bash
python manage.py runserver
# or
export DJANGO_SETTINGS_MODULE=zim_rentals.settings && daphne -b 0.0.0.0 -p 8000 zim_rentals.asgi:application
```

7. Set up Redis (required for WebSockets and Celery):

```bash
sudo apt-get install redis-server  # For Ubuntu/Debian
# For other systems, see Redis documentation
```

8. Run Celery worker (for price alerts and scheduled tasks):

```bash
celery -A zim_rentals worker -l info
```

9. Run Celery beat (for periodic tasks):

```bash
celery -A zim_rentals beat -l info
```

## Price Alerts Setup

The Price Alerts feature allows users to:

-   Save search criteria for properties
-   Receive email notifications when new matching listings are posted
-   Receive real-time in-app notifications via WebSockets
-   View all their saved searches

This feature requires:

-   Redis for WebSocket communication and as Celery broker
-   Celery for background task processing and scheduled checks

## API Documentation

Zim Rentals provides a RESTful API for integrating with other applications or building custom clients.

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Obtain a token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

2. Use the token in subsequent requests:

```bash
curl -X GET http://127.0.0.1:8000/api/listings/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

3. Refresh token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

### Endpoints

#### Listings

-   `GET /api/listings/` - List all listings
-   `POST /api/listings/` - Create a new listing (requires authentication)
-   `GET /api/listings/{id}/` - Get details for a specific listing
-   `PUT /api/listings/{id}/` - Update a listing (owner only)
-   `DELETE /api/listings/{id}/` - Delete a listing (owner only)
-   `POST /api/listings/{id}/favorite/` - Favorite a listing
-   `POST /api/listings/{id}/unfavorite/` - Unfavorite a listing
-   `GET /api/listings/favorites/` - Get user's favorited listings

#### Listing Images

-   `GET /api/listing-images/` - List all images
-   `POST /api/listing-images/` - Upload a new image (for listing owner)
-   `GET /api/listing-images/{id}/` - Get a specific image
-   `DELETE /api/listing-images/{id}/` - Delete an image (owner only)

#### Favorites

-   `GET /api/favorites/` - List user's favorites
-   `POST /api/favorites/` - Create a new favorite
-   `DELETE /api/favorites/{id}/` - Remove a favorite

#### Chat Messages

-   `GET /api/listings/{id}/messages/` - Get all messages for a listing
-   `POST /api/listings/{id}/messages/` - Send a message for a listing
-   `GET /api/listings/{id}/messages/{message_id}/` - Get a specific message
-   `POST /api/listings/{id}/messages/{message_id}/mark_read/` - Mark a message as read

### Examples

#### Creating a listing:

```bash
curl -X POST http://127.0.0.1:8000/api/listings/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cozy apartment in Harare",
    "description": "Beautiful 2-bedroom apartment",
    "price": 150.00,
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

#### Sending a chat message:

```bash
curl -X POST http://127.0.0.1:8000/api/listings/4/messages/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message": "I am interested in this property. Is it still available?"}'
```

### Response Format

All API responses are returned in JSON format. Successful responses typically include the requested data or a confirmation message. Error responses include an appropriate HTTP status code and an error message.

Example success response:

```json
{
	"id": 4,
	"title": "Kitchen",
	"description": "a small kitchen for a single bachelor",
	"price": "35.00",
	"currency": "USD",
	"landlord": 5,
	"landlord_details": {
		"id": 5,
		"username": "Harry",
		"email": "harry@gmail.com"
	},
	"city": "masvingo",
	"suburb": "Rujeko"
}
```

Example error response:

```json
{
	"detail": "Authentication credentials were not provided."
}
```

## Technologies Used

-   Django
-   Bootstrap 5
-   PostgreSQL (recommended for production)
-   Django Allauth for authentication
-   Django Crispy Forms for form rendering
-   Django Geoposition for location services
-   Channels for WebSockets
-   Celery with Redis for background tasks and notifications
-   Django REST Framework for API endpoints
-   Simple JWT for API authentication
