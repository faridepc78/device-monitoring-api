# Device Monitoring API

A small REST API for managing monitoring devices, receiving telemetry data, viewing device telemetry history, and creating temperature alerts.

## Tech Stack

- Python 3.13
- Django 6.1.1
- Django REST Framework 3.18.1
- PostgreSQL 18
- psycopg 3.3.6
- drf-spectacular 0.30.0
- Docker / Docker Compose

## Project Structure

```text
device-monitoring-api/
├── config/
│   ├── settings.py
│   └── urls.py
├── monitoring/
│   ├── management/
│   │   └── commands/
│   │       └── export_project.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── docs/
│   └── Device-Monitoring-API.postman_collection.json
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── README.md
└── requirements.txt
```

## Features

- Device CRUD
- Telemetry ingestion
- Telemetry validation
- Latest telemetry for a device
- Telemetry history with date filtering
- Pagination for telemetry history
- Automatic high-temperature alert creation
- Alert listing
- PostgreSQL database
- Automated API tests
- OpenAPI schema generation
- Swagger UI documentation
- Postman collection for API testing
- Docker support
- Project export management command

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
DB_NAME=device_monitoring
DB_USER=device_monitoring_user
DB_PASSWORD=device_monitoring_pass
DB_HOST=localhost
DB_PORT=5432

DJANGO_SECRET_KEY=django-insecure-change-me
```

The real `.env` file is ignored by Git.

## Local Installation

### 1. Create a virtual environment

```bash
python -m venv venv
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL

Create the database and user:

```sql
CREATE DATABASE device_monitoring;
CREATE USER device_monitoring_user WITH PASSWORD 'device_monitoring_pass';
GRANT ALL PRIVILEGES ON DATABASE device_monitoring TO device_monitoring_user;
```

Connect to the `device_monitoring` database and grant access to the public schema:

```sql
GRANT ALL ON SCHEMA public TO device_monitoring_user;
```

Update `.env` if different database credentials are used.

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## Run With Docker

Build and start the project:

```bash
docker compose up --build
```

The application waits for the database health check, applies migrations, and then starts the Django development server.

The API will be available at:

```text
http://127.0.0.1:8000/
```

To stop the containers:

```bash
docker compose down
```

## API Documentation

Swagger UI is available at:

```text
http://127.0.0.1:8000/api/docs/
```

The OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

## Postman Collection

A Postman collection containing all main API endpoints is included in:

```text
docs/Device-Monitoring-API.postman_collection.json
```

Import the file into Postman to test the API endpoints.

The collection uses one collection-level variable:

```text
base_url = http://127.0.0.1:8000
```

## API Endpoints

### Devices

#### List devices

```http
GET /api/devices/
```

#### Create a device

```http
POST /api/devices/
```

Example request:

```json
{
  "name": "Inverter 001",
  "code": "INV-001",
  "is_active": true
}
```

#### Retrieve a device

```http
GET /api/devices/{id}/
```

#### Update a device

```http
PATCH /api/devices/{id}/
```

#### Delete a device

```http
DELETE /api/devices/{id}/
```

#### Latest telemetry

```http
GET /api/devices/{id}/latest/
```

#### Telemetry history

```http
GET /api/devices/{id}/telemetry/
```

Filter by date range:

```http
GET /api/devices/{id}/telemetry/?from=2026-10-01&to=2026-10-04
```

Telemetry history is paginated.

### Telemetry

#### Create telemetry

```http
POST /api/telemetry/
```

Example request:

```json
{
  "device_code": "INV-001",
  "temperature": 42.5,
  "power": 1250,
  "voltage": 380,
  "timestamp": "2026-10-04T10:00:00Z"
}
```

Telemetry is accepted only for an active device with the supplied `device_code`.

### Alerts

#### List alerts

```http
GET /api/alerts/
```

## Alert Logic

When telemetry is received with:

```text
temperature > 70
```

a `high_temperature` alert is automatically created for the device.

Each alert contains:

- Device
- Alert type
- Recorded temperature value
- Creation time
- Resolved/unresolved status

Telemetry creation and alert creation are handled in the service layer instead of being placed directly in the views.

## Validation

The API validates the main input cases:

- `device_code` must belong to an active device.
- `power` cannot be negative.
- `voltage` cannot be negative.
- `from` cannot be later than `to` in telemetry history queries.
- Standard Django REST Framework validation is used for required fields and field types.

Invalid input returns an appropriate HTTP error response.

## Design Decisions

### Service Layer

Telemetry creation and high-temperature alert creation are handled by a small service layer.

This keeps business logic out of the views and makes the code easier to understand, maintain, and test.

### Database Relationships

`Telemetry` and `Alert` reference `Device` using foreign keys.

A device can have many telemetry records and many alerts.

### Database Index

A composite database index is defined on:

```text
device + timestamp
```

This supports the common access pattern of querying telemetry for a specific device by time.

### Device Code for Telemetry Ingestion

Telemetry requests use `device_code` instead of requiring clients to know the internal database ID of a device.

### Pagination

Telemetry history is paginated to avoid returning an unbounded number of records in a single response.

### Alert Threshold

The temperature threshold is defined as a named constant in the service layer instead of being repeated throughout the application.

## Automated Tests

Tests cover:

- Device creation
- Telemetry creation
- Latest telemetry retrieval
- Latest telemetry when no telemetry exists
- Telemetry history date filtering
- High-temperature alert creation
- Invalid device code
- Negative power validation

Run all tests with:

```bash
python manage.py test
```

## Project Export Command

A custom Django management command is included to export a clean ZIP archive of the project source code.

Run:

```bash
python manage.py export_project
```

The generated ZIP excludes local or unnecessary files such as:

- `.env`
- `venv`
- `.git`
- `.idea`
- `.vscode`
- `__pycache__`
- Python bytecode files
- Existing ZIP files

## Notes

This project is intentionally kept small and focused on the requirements of the technical task. It avoids unnecessary infrastructure and abstractions while keeping the code readable and extensible.
