# Organization Management Service

A multi-tenant organization management backend built with FastAPI and MongoDB. This service provides CRUD operations for organizations with dynamic collection creation, JWT-based authentication, and secure admin management.

## Features

- **Multi-tenant Architecture**: Each organization gets its own MongoDB collection (`org_<organization_name>`)
- **Master Database**: Centralized metadata and admin credentials storage
- **JWT Authentication**: Secure token-based authentication for admin operations
- **Dynamic Collection Management**: Automatic collection creation, migration, and deletion
- **RESTful API**: Clean, well-documented API endpoints
- **Comprehensive Tests**: Full test coverage with pytest
- **Docker Support**: Easy deployment with Docker Compose

## Architecture

The service uses a master database approach where:
- **Master Database** (`org_master`): Stores organization metadata and admin credentials
- **Organization Collections**: Dynamic collections named `org_<sanitized_name>` for each organization's data

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- MongoDB 7.0+ (if running without Docker)

## Deployment on Render

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

Quick steps:
1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables (MONGODB_URL, JWT_SECRET_KEY)
4. Deploy!

## Quick Start

### Using Docker Compose with MongoDB Atlas (Recommended)

1. **Create a `.env` file** with your MongoDB Atlas connection string:
```bash
# .env file
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
MONGODB_DB_NAME=org_master
JWT_SECRET_KEY=your-secret-key-change-in-production
```

2. **Start the API service** (MongoDB Atlas is used, local MongoDB is not needed):
```bash
docker-compose up --build api
```

The API will be available at `http://localhost:8000`

### Using Docker Compose with Local MongoDB

1. **Create a `.env` file** (optional, defaults are provided):
```bash
cp .env.example .env
# Edit .env with your settings
```

2. **Start all services** (including local MongoDB):
```bash
docker-compose --profile local-db up --build
```

The API will be available at `http://localhost:8000`

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up MongoDB**:
   - **Option A: Use MongoDB Atlas** (Recommended)
     - Create a `.env` file with your MongoDB Atlas connection string:
     ```bash
     MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
     MONGODB_DB_NAME=org_master
     JWT_SECRET_KEY=your-secret-key
     ```
   
   - **Option B: Use Local MongoDB**
     ```bash
     # Using Docker
     docker run -d -p 27017:27017 --name mongodb mongo:7.0
     
     # Or use your local MongoDB instance
     # Then set environment variables:
     export MONGODB_URL="mongodb://localhost:27017"
     export MONGODB_DB_NAME="org_master"
     export JWT_SECRET_KEY="your-secret-key"
     ```

3. **Run the application**:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Create Organization
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Acme Corp",
    "email": "admin@acme.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "message": "Organization created successfully",
  "organization": {
    "organization_name": "Acme Corp",
    "collection_name": "org_acme_corp",
    "admin": {
      "admin_id": "...",
      "email": "admin@acme.com"
    },
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### Get Organization
```bash
curl "http://localhost:8000/org/get?organization_name=Acme%20Corp"
```

### Login
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Update Organization
```bash
curl -X PUT "http://localhost:8000/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "organization_name": "Acme Corp",
    "new_organization_name": "Acme Corporation",
    "email": "newadmin@acme.com"
  }'
```

### Delete Organization
```bash
curl -X DELETE "http://localhost:8000/org/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "organization_name": "Acme Corp"
  }'
```

## Testing

### Run Tests with Docker

```bash
# Start services
docker-compose up -d mongodb

# Run tests
docker-compose run --rm api pytest tests/ -v
```

### Run Tests Locally

```bash
# Install test dependencies
pip install -r requirements.txt

# Set test environment
export MONGODB_URL="mongodb://localhost:27017"
export MONGODB_DB_NAME="org_master_test"
export JWT_SECRET_KEY="test-secret-key"

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Test Coverage

The test suite covers:
- ✅ Organization creation (success and duplicate name handling)
- ✅ Organization retrieval
- ✅ Admin authentication (success and failure cases)
- ✅ Organization deletion (with authorization checks)
- ✅ Organization updates (rename, email, password)
- ✅ Collection migration during rename

## Management CLI

Use the management script to list organizations and admins:

```bash
# List all organizations
python scripts/manage.py list-orgs

# List all admin accounts
python scripts/manage.py list-admins

# List all organization collections
python scripts/manage.py list-collections
```

## Environment Variables

See `.env.example` for all available environment variables:

- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Master database name
- `JWT_SECRET_KEY`: Secret key for JWT token signing (change in production!)
- `JWT_EXPIRATION_HOURS`: Token expiration time in hours
- `DEBUG`: Enable debug mode

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth_routes.py      # Authentication endpoints
│   │       └── org_routes.py       # Organization endpoints
│   ├── auth/
│   │   ├── jwt_handler.py          # JWT token creation/verification
│   │   └── password.py             # Password hashing
│   ├── core/
│   │   └── config.py               # Configuration management
│   ├── db/
│   │   └── mongo.py                # MongoDB client and helpers
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   ├── repositories/
│   │   ├── master_repo.py          # Master DB operations
│   │   └── org_repo.py             # Organization collection operations
│   ├── services/
│   │   └── org_service.py          # Business logic
│   ├── utils/
│   │   └── helpers.py              # Utility functions
│   └── main.py                     # FastAPI application
├── tests/
│   ├── test_auth.py
│   ├── test_org_create.py
│   ├── test_org_delete.py
│   ├── test_org_get.py
│   └── test_org_update.py
├── scripts/
│   └── manage.py                   # Management CLI
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens include expiration
- Organization operations require authentication
- Admins can only access their own organization
- Input sanitization for organization names
- Collection name validation

## Future Improvements

- Rate limiting middleware
- Enhanced logging and monitoring
- Database connection pooling optimization
- Support for multiple admins per organization
- Organization-level permissions and roles
- Audit logging
- Backup and restore functionality

## License

This project is provided as-is for demonstration purposes.

