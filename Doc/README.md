# Mini ERP System 🚀

A comprehensive Enterprise Resource Planning (ERP) system built with Flask (Backend), React (Frontend), and PostgreSQL database. This system manages Inventory, Sales, Purchase, User Management, and Reporting modules with modern development practices.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### ✅ Implemented Features

#### User Management & Authentication (Phase 2)
- ✅ JWT-based authentication (access + refresh tokens)
- ✅ User registration with email validation
- ✅ Secure login/logout
- ✅ Role-based access control (Admin, Manager, Staff)
- ✅ Permission-based authorization
- ✅ Profile management (view/update)
- ✅ Password change functionality
- ✅ Token refresh mechanism
- ✅ Account status management (active/inactive)

#### Database Models (Phase 1)
- ✅ User, Role, Permission models with RBAC
- ✅ Category model with hierarchical structure
- ✅ Product model with pricing and stock tracking
- ✅ Warehouse model for multi-location inventory
- ✅ Stock model with quantity tracking
- ✅ StockMovement model for audit trail
- ✅ Customer model with billing/shipping addresses
- ✅ SalesOrder, SalesOrderItem, Invoice, Payment models
- ✅ Supplier model with bank details
- ✅ PurchaseOrder, PurchaseOrderItem, Bill models
- ✅ Timestamp and soft delete mixins
- ✅ Database migrations with Alembic

### 🚧 Planned Features

#### Inventory Management API (Phase 3 - Completed)
- Category CRUD endpoints
- Product CRUD endpoints with search and filters
- Low stock API endpoint
- Warehouse CRUD endpoints
- Stock listing API with filters
- Stock movement APIs (IN, OUT, TRANSFER, ADJUSTMENT)
- Stock movement tracking endpoint

#### Sales Management (Phase 4)
- Sales order processing
- Invoice generation
- Payment tracking
- Customer management

#### Purchase Management (Phase 5)
- Purchase order creation
- Supplier management
- Bill processing
- Goods receiving

#### Reporting & Analytics (Phase 11)
- Dashboard with KPIs
- Sales reports
- Inventory reports
- Financial reports

#### Advanced Features (Phase 15)
- PDF generation for invoices
- Excel/CSV import/export
- Email notifications
- File upload support

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Migrations**: Flask-Migrate (Alembic)
- **Validation**: Marshmallow
- **Testing**: pytest, pytest-flask
- **Caching**: Redis
- **Task Queue**: Celery (Phase 15)

### Frontend (Phase 6+)
- **Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit
- **Routing**: React Router
- **UI Library**: Tailwind CSS
- **Forms**: React Hook Form + Yup
- **Charts**: Chart.js / Recharts
- **HTTP Client**: Axios with React Query
- **Testing**: Jest, React Testing Library, Cypress

### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry (Phase 14)
- **Logging**: ELK Stack / CloudWatch (Phase 14)
- **Server**: Gunicorn (production)

## 📁 Project Structure

```
mini-erp/
├── backend/                    # Flask backend application
│   ├── app.py                 # Main application entry point
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend Docker image
│   ├── models/               # SQLAlchemy models
│   ├── routes/               # API endpoints (blueprints)
│   ├── services/             # Business logic layer
│   ├── auth/                 # Authentication & authorization
│   ├── middleware/           # Custom middleware
│   ├── validators/           # Input validation schemas
│   ├── utils/                # Helper functions
│   ├── migrations/           # Database migrations (Alembic)
│   ├── tests/                # Backend tests
│   └── uploads/              # File uploads directory
├── frontend/                  # React frontend (Phase 6+)
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   ├── store/            # Redux store
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript type definitions
│   │   └── utils/            # Helper functions
│   ├── public/               # Static assets
│   └── tests/                # Frontend tests
├── docs/                      # Documentation (Phase 13)
│   ├── api/                  # API documentation
│   ├── user-guide/           # User guides
│   └── developer-guide/      # Developer documentation
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # CI/CD pipeline
├── docker-compose.yml        # Production compose
├── docker-compose.dev.yml    # Development compose
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/)) - for frontend (Phase 6+)
- **PostgreSQL 15+** ([Download](https://www.postgresql.org/download/)) - or use Docker
- **Git** ([Download](https://git-scm.com/downloads))
- **Docker & Docker Compose** (Optional but recommended) ([Download](https://www.docker.com/))

### Verify Installation

```bash
python --version   # Should be 3.11+
node --version     # Should be 18+
npm --version
git --version
docker --version
docker-compose --version
```

## 🚀 Installation

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Flask Project"
   ```

2. **Create environment file**
   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Edit `.env` file** with your configuration
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Start services with Docker**
   ```bash
   # Start database and redis only (for development)
   docker-compose -f docker-compose.dev.yml up -d
   
   # OR start all services including backend
   docker-compose up -d
   ```

5. **Initialize database** (if not using full docker-compose)
   ```bash
   cd backend
   flask db upgrade
   ```

### Option 2: Local Installation (Without Docker)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "Flask Project"
   ```

2. **Set up PostgreSQL database**
   ```sql
   -- In PostgreSQL shell
   CREATE DATABASE mini_erp_db;
   CREATE USER erp_user WITH PASSWORD 'erp_password';
   GRANT ALL PRIVILEGES ON DATABASE mini_erp_db TO erp_user;
   ```

3. **Create Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file**
   ```bash
   cp .env.example .env
   ```

6. **Edit `.env` file** with your database credentials and secret keys

7. **Initialize database**
   ```bash
   flask db upgrade
   ```

## 🏃 Running the Application

### Using Docker

```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f backend

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down
```

Access the application:
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

### Local Development

```bash
cd backend

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run Flask development server
flask run --debug
# OR
python app.py
```

Access the application:
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## 🔧 Development Workflow

### Creating a New Feature

1. **Create a feature branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project structure

3. **Write tests** for your feature
   ```bash
   pytest tests/test_your_feature.py
   ```

4. **Run all tests**
   ```bash
   pytest --cov=. --cov-report=html
   ```

5. **Check code quality**
   ```bash
   black .                    # Format code
   flake8 .                   # Check style
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat(module): description of your feature"
   ```

7. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
- `feat(auth): add JWT token refresh mechanism`
- `fix(inventory): correct stock calculation on order cancellation`
- `docs(api): add examples to sales endpoints`
- `test(purchase): add integration tests for PO creation`

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_user_registration

# View coverage report
# Open htmlcov/index.html in browser
```

### Test Structure

```
backend/tests/
├── unit/              # Unit tests
│   ├── test_models.py
│   └── test_services.py
├── integration/       # Integration tests
│   └── test_api.py
├── fixtures/          # Test fixtures
│   └── conftest.py
└── test_config.py     # Test configuration
```

## 📚 API Documentation

### Current Endpoints (Phase 2)

#### System Health
```bash
GET /api/health              # Health check endpoint
GET /                        # Root endpoint
```

#### Authentication & Authorization
```bash
POST /api/auth/register      # Register new user
POST /api/auth/login         # Login and get tokens
POST /api/auth/refresh       # Refresh access token
POST /api/auth/logout        # Logout (requires token)
GET  /api/auth/me            # Get current user profile
PUT  /api/auth/me            # Update user profile
POST /api/auth/change-password  # Change password
GET  /api/auth/verify-token  # Verify token validity
```

**📖 Full API Documentation:**
- See [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md) for detailed endpoint specifications
- Includes request/response examples, error codes, and usage patterns

### Example API Usage

**Register a new user:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'
```

**Access protected endpoint:**
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

### Test Users (from database seed)

After running the seed script, these users are available:
- **Admin**: `admin` / `admin123` (all permissions)
- **Manager**: `manager` / `manager123` (all except user management)
- **Staff**: `staff` / `staff123` (read + basic operations)

### Phase 3 Inventory Endpoints (Implemented)

```bash
# Inventory Management (Phase 3)
GET    /api/inventory/categories            # List categories
POST   /api/inventory/categories            # Create category (auth required)
GET    /api/inventory/categories/{id}       # Get category
PUT    /api/inventory/categories/{id}       # Update category (auth required)
DELETE /api/inventory/categories/{id}       # Deactivate category (auth required)

GET    /api/inventory/products              # List/search products
POST   /api/inventory/products              # Create product (auth required)
GET    /api/inventory/products/{id}         # Get product
PUT    /api/inventory/products/{id}         # Update product (auth required)
DELETE /api/inventory/products/{id}         # Deactivate product (auth required)
GET    /api/inventory/products/low-stock    # Get low stock products

GET    /api/inventory/warehouses            # List/search warehouses
POST   /api/inventory/warehouses            # Create warehouse (auth required)
GET    /api/inventory/warehouses/{id}       # Get warehouse
PUT    /api/inventory/warehouses/{id}       # Update warehouse (auth required)
DELETE /api/inventory/warehouses/{id}       # Deactivate warehouse (auth required)

GET    /api/inventory/stocks                # List stock with filters
GET    /api/inventory/stocks/movements      # List stock movement logs
POST   /api/inventory/stocks/movement       # Record stock movement (auth required)
```

### Coming Soon (Phase 4+)

```bash
# Sales Management
POST   /api/sales/orders               # Create sales order
GET    /api/sales/orders               # List sales orders

# Purchase Management
POST   /api/purchase/orders            # Create purchase order
GET    /api/purchase/orders            # List purchase orders
```

## 🚢 Deployment

### Deploying with Docker

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.yml build
   ```

2. **Set production environment variables**
   ```bash
   export SECRET_KEY="your-production-secret"
   export JWT_SECRET_KEY="your-production-jwt-secret"
   ```

3. **Start production services**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Deploying to Cloud Platforms

See [docs/deployment/](docs/deployment/) for detailed deployment guides:
- Heroku
- DigitalOcean
- AWS (EC2, RDS, S3)
- Azure
- Google Cloud Platform

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Write tests for new features
- Update documentation
- Use meaningful commit messages
- Keep Pull Requests focused and small

## 📖 Learning Resources

### Backend (Flask)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)

### Database
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://testdriven.io/courses/)

### Docker
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## 📋 Development Phases

### ✅ Completed Phases

- [x] **Phase 0**: Project Foundation & Setup ✅ *(Completed: March 8, 2026)*
  - Complete project structure with backend folders
  - Flask application with factory pattern
  - Configuration system (Dev/Test/Prod)
  - Virtual environment with dependencies
  - Docker configuration (PostgreSQL, Redis)
  - CI/CD pipeline with GitHub Actions
  - Testing infrastructure with pytest
  - Comprehensive documentation

- [x] **Phase 1**: Database Design & Implementation ✅ *(Completed: March 9, 2026)*
  - 14 database models implemented
  - Base mixins (TimestampMixin, SoftDeleteMixin)
  - User Management: User, Role, Permission with RBAC
  - Inventory: Category, Product, Warehouse, Stock, StockMovement
  - Sales: Customer, SalesOrder, SalesOrderItem, Invoice, Payment
  - Purchase: Supplier, PurchaseOrder, PurchaseOrderItem, Bill
  - Flask-Migrate setup with initial migration
  - Database seeding script with sample data
  - 31 model unit tests - All passing ✅
  - See [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) for details

- [x] **Phase 2**: Authentication & Authorization Backend ✅ *(Completed: March 10, 2026)*
  - JWT-based authentication system
  - 9 authentication endpoints (register, login, refresh, logout, profile, etc.)
  - Authorization decorators (@token_required, @role_required, @permission_required)
  - Password hashing and validation
  - Token refresh mechanism
  - User profile management
  - 14 authentication tests - All passing ✅
  - Complete API documentation
  - See [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md) for details

- [x] **Phase 3**: Inventory Management Backend API ✅ *(Completed: March 13, 2026)*
   - Category CRUD operations with validation
   - Product CRUD operations with search/filter/low stock support
   - Warehouse CRUD operations
   - Stock listing API with product/warehouse filtering
   - Stock movement API (IN, OUT, TRANSFER, ADJUSTMENT)
   - Stock movement tracking endpoint
   - 12 inventory API tests added
   - See [PHASE_3_COMPLETE.md](PHASE_3_COMPLETE.md) for details

**Total Tests: 57 passing (expected after test run)** 🎉

### 🚧 Upcoming Phases

- [ ] **Phase 4**: Sales Management Backend API
- [ ] **Phase 5**: Purchase Management Backend API
- [ ] **Phase 6**: Frontend Foundation & Setup
- [ ] **Phase 7**: Authentication Frontend
- [ ] **Phase 8**: Inventory Management Frontend
- [ ] **Phase 9**: Sales Management Frontend
- [ ] **Phase 10**: Purchase Management Frontend
- [ ] **Phase 11**: Dashboard & Reporting
- [ ] **Phase 12**: Testing & Quality Assurance
- [ ] **Phase 13**: Documentation
- [ ] **Phase 14**: Deployment & DevOps
- [ ] **Phase 15**: Advanced Features

## 🐛 Known Issues

No known issues at this time. Please report bugs in the [Issues](../../issues) section.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work*

## 🙏 Acknowledgments

- Flask community for the excellent framework
- All contributors who help improve this project

## 📞 Support

For support, please:
- Create an [Issue](../../issues)
- Contact: your-email@example.com

---

**Happy Coding! 🎉**
