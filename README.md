# Address Book App

A FastAPI-based Address Book API for storing and querying address entries with validation, geolocation filtering.

## Overview

This project provides a REST API to create, read, update, and delete address records. It includes support for:

- ISO 3166-1 alpha-2 country validation
- E.164 phone number validation
- Postal code format validation
- Asynchronous SQLite database access via SQLAlchemy AsyncIO
- Optional nearby address filtering using latitude/longitude and radius
- Optional filtering by name, administrative_area, postal_code, and country
- Auto-generated Swagger UI and Redoc documentation

## Features

- `GET /api/addresses` - list addresses with pagination and optional filters
- `POST /api/addresses` - create an address with validation
- `GET /api/addresses/{address_uuid}` - read a single address
- `PUT /api/addresses/{address_uuid}` - update an address
- `DELETE /api/addresses/{address_uuid}` - remove an address
- `GET /docs` - interactive Swagger UI
- `GET /redoc` - Redoc API documentation

## Architecture

- `main.py` - FastAPI application factory and startup lifecycle
- `core/config.py` - environment-driven application settings
- `infrastructure/database.py` - async database engine, session management, and schema initialization
- `core/models.py` and `core/mixins.py` - shared SQLAlchemy base classes and mixins
- `modules/address/models.py` - SQLAlchemy address model
- `modules/address/schemas.py` - Pydantic schemas and field validation
- `modules/address/services.py` - CRUD and geospatial query logic
- `modules/address/routers.py` - API route declarations

## Requirements

- Python 3.14+
- FastAPI
- SQLAlchemy AsyncIO
- pydantic-settings
- phonenumbers
- pycountry
- aiosqlite (for SQLite async support)

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows
# or
source .venv/bin/activate       # macOS / Linux
```

> If you use `uv` to manage the project environment, install dependencies from the uv environment instead:
>
> ```bash
> uv sync
> ```
>
> This will automatically create a virtual environment for you, as well as install dependencies (no need to do step #2).

2. Install dependencies.

```bash
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
DATABASE_URI=sqlite+aiosqlite:///./db.sqlite3
API_PREFIX=/api
DEBUG=True
LOG_LEVEL=INFO
```

## Running the application

Start the app with Uvicorn:

```bash
python main.py
```

The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

### Create an address

```http
POST /api/addresses
Content-Type: application/json
```

Example payload:

```json
{
  "name": "Home",
  "street": "123 Main St",
  "sub_locality": "Downtown",
  "locality": "Springfield",
  "administrative_area": "IL",
  "postal_code": "62701",
  "country": "US",
  "latitude": 39.7817,
  "longitude": -89.6501,
  "notes": "Primary residence",
  "email": "example@example.com",
  "phone_number": "+12175551234",
  "website": "https://example.com"
}
```

### List addresses

```http
GET /api/addresses?skip=0&limit=100
```

### Query addresses with filters

```http
GET /api/addresses?name=Home&admin_area=IL&postal_code=62701&country=US
```

### Query nearby addresses

```http
GET /api/addresses?lat=39.78&lon=-89.65&radius=5
```

### Retrieve, update, delete

- `GET /api/addresses/{address_uuid}`
- `PUT /api/addresses/{address_uuid}`
- `DELETE /api/addresses/{address_uuid}`

## Validation rules

- `country` must be an ISO 3166-1 alpha-2 code (e.g. `US`, `DE`).
- `phone_number` must use E.164 format and start with `+`.
- `postal_code` accepts letters, numbers, spaces, and hyphens.

## Database

The app initializes the SQLite database automatically during startup by creating the required tables from SQLAlchemy metadata.

## Testing

Install the test tools and run pytest:

```bash
python -m pip install pytest pytest-asyncio httpx
pytest -q
```

If you use `uv` for the environment, install the test tools from the uv environment instead:

```bash
uv run python -m pip install pytest pytest-asyncio httpx
uv run pytest -q
```

The test suite uses a repository-root `test_db.sqlite3` database file and resets it before each test session.

## Notes

- In production, configure explicit CORS origins instead of allowing all origins.
- The default database is SQLite; the application can be adapted to other SQLAlchemy-supported databases.
