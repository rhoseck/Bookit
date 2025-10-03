# BookIt API

A REST API for a bookings platform where users can browse services, make bookings, and leave reviews, while admins manage services and bookings.

## Architecture Decisions
- **Framework**: FastAPI for its async support, automatic OpenAPI docs, and Pydantic integration.
- **Database**: PostgreSQL chosen for its relational integrity (e.g., foreign keys for bookings), robust support for migrations via Alembic, and performance for structured data.
- **Authentication**: JWT with bcrypt for password hashing, ensuring secure authentication and role-based authorization.
- **Modular Design**: Separated into routers (API endpoints), services (business logic), and repositories (DB access) for maintainability.
- **Identifiers**: UUIDs used as primary keys for all entities (users, services, bookings, reviews) for better security, scalability, and distributed system compatibility.

## Database Choice
PostgreSQL was chosen because:
- It enforces referential integrity (e.g., `user_id` and `service_id` in bookings).
- Alembic provides robust migration management.
- It handles concurrent booking checks efficiently with proper indexing.
- Native UUID support for secure, globally unique identifiers.

## UUID Migration
The application was migrated from integer primary keys to UUIDs for enhanced security and scalability:
- **Migration**: A destructive migration (`e8105d38b481`) was created to rebuild all tables with UUID primary and foreign keys.
- **Impact**: All entity IDs are now UUIDs (users, services, bookings, reviews).
- **API Changes**: All endpoints now expect and return UUID identifiers.
- **Security**: UUIDs prevent enumeration attacks and provide better distributed system compatibility.

## Running Locally

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Git

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd BookIt
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE bookit;
   CREATE USER bookit_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE bookit TO bookit_user;
   ```

5. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://bookit_user:your_password@localhost:5432/bookit
   JWT_SECRET=your-super-secret-jwt-key-here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

8. **Access the application:**
   - API: http://localhost:8080
   - Interactive API Docs: http://localhost:8080/docs
   - Alternative Docs: http://localhost:8080/redoc

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | None | ✅ |
| `JWT_SECRET` | Secret key for JWT token signing | None | ✅ |
| `JWT_ALGORITHM` | Algorithm for JWT encoding | `HS256` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time | `60` | ❌ |

## Authentication & Authorization

### User Roles
- **User**: Can create bookings, view own bookings, create reviews
- **Admin**: Full system access, can manage all bookings, services, and users

### Role-Based Permissions
- **Service Management**: Admin only (create, update, delete)
- **Booking Management**: Admin only (update, delete) | Users (create, view own)
- **User Management**: Admin can view all users | Users can view/update own profile
- **Reviews**: Users can create/edit own reviews | Admin can manage all reviews

### Authentication Flow
1. Register with `/auth/register` (creates User role by default)
2. Login with `/auth/login` to receive JWT token
3. Include token in `Authorization: Bearer <token>` header
4. Admins must be promoted manually via database update

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI Schema**: http://localhost:8080/openapi.json

### Main Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user

#### Users
- `GET /me` - Get current user profile
- `PATCH /me` - Update current user profile

#### Services (Public read, Admin manage)
- `GET /services` - List services (with filters)
- `GET /services/{id}` - Get service details
- `POST /services` - Create service (Admin only)
- `PATCH /services/{id}` - Update service (Admin only)
- `DELETE /services/{id}` - Delete service (Admin only)

#### Bookings
- `POST /bookings` - Create booking (Authenticated users)
- `GET /bookings/me` - List user's own bookings (Authenticated users)
- `GET /bookings` - List all bookings (Admin only)
- `GET /bookings/{id}` - Get booking details (Owner or Admin)
- `PATCH /bookings/{id}` - Update booking (Admin only)
- `DELETE /bookings/{id}` - Cancel booking (Admin only)

#### Reviews
- `POST /reviews` - Create review
- `GET /services/{id}/reviews` - Get service reviews
- `PATCH /reviews/{id}` - Update review
- `DELETE /reviews/{id}` - Delete review

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_auth.py
```

## Deployment

### Deploying to Render (Recommended)

Render provides a simple, automated deployment process for the BookIt API.

#### Prerequisites
- GitHub account with your BookIt repository
- Render account (free tier available)

#### Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Review the configuration and click "Apply"

3. **Automatic Setup**:
   Render will automatically:
   - Create a PostgreSQL database
   - Set up environment variables
   - Install dependencies
   - Run database migrations
   - Deploy your API

#### Manual Deployment (Alternative)

If you prefer manual setup:

1. **Create Web Service**:
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `./start.sh`
     - **Environment**: `Python 3`

2. **Create Database**:
   - Click "New +" → "PostgreSQL"
   - Choose a name (e.g., `bookit-db`)
   - Note the connection details

3. **Set Environment Variables**:
   In your web service settings, add:
   ```
   DATABASE_URL=<your-postgres-connection-string>
   JWT_SECRET=<generate-secure-random-key>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

#### Environment Variables for Production

| Variable | Value | Source |
|----------|-------|---------|
| `DATABASE_URL` | PostgreSQL connection string | From Render PostgreSQL service |
| `JWT_SECRET` | Secure random key (32+ chars) | Generate with `openssl rand -hex 32` |
| `JWT_ALGORITHM` | `HS256` | Fixed value |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Recommended for production |

### Production URLs

After deployment, your API is available at:
- **Base URL**: `https://bookit-dze3.onrender.com`
- **API Documentation**: `https://bookit-dze3.onrender.com/docs`
- **Alternative Docs**: `https://bookit-dze3.onrender.com/redoc`

### Live Demo

The BookIt API is currently deployed and accessible:
- **Host**: Render.com
- **Base URL**: https://bookit-dze3.onrender.com
- **Database**: PostgreSQL on Render (Free Tier)
- **Auto-deploy**: Enabled on `main` branch pushes

### Deployment Features

✅ **Automatic HTTPS** - Render provides SSL certificates  
✅ **Auto-deployments** - Deploys on every push to main branch  
✅ **Environment isolation** - Separate staging/production environments  
✅ **Database backups** - Automatic PostgreSQL backups  
✅ **Monitoring** - Built-in health checks and monitoring  
✅ **Custom domains** - Add your own domain name  

### Alternative Deployment Options

#### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t bookit-api .
docker run -p 8000:8000 bookit-api
```

#### Manual Server Deployment
Use the provided `deploy.sh` script for Ubuntu/Debian servers:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Project Structure
```
BookIt/
├── app/
│   ├── api/
│   │   └── routers/          # API route handlers
│   ├── core/                 # Core configuration and utilities
│   ├── db/                   # Database models and connection
│   ├── repositories/         # Database access layer
│   ├── schemas/              # Pydantic models for validation
│   ├── services/             # Business logic layer
│   └── tests/                # Test files
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
└── README.md                # This file
```