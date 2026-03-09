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

### Core Modules
- **User Management**: Authentication, authorization, role-based access control (RBAC)
- **Inventory Management**: Products, categories, stock tracking, warehouse management
- **Sales Management**: Customers, sales orders, invoicing, payment tracking
- **Purchase Management**: Suppliers, purchase orders, goods receiving, bill management
- **Reporting & Analytics**: Dashboard with KPIs, sales reports, inventory reports

### Technical Features
- JWT-based authentication
- RESTful API design
- Database migrations with Alembic
- File upload support (images, documents)
- PDF generation for invoices and reports
- Excel/CSV import/export
- Role-based permissions
- Comprehensive error handling
- Docker containerization
- CI/CD pipeline with GitHub Actions

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

Once the API is running, access the documentation:

- **Swagger UI**: http://localhost:5000/api/docs (Phase 3+)
- **ReDoc**: http://localhost:5000/api/redoc (Phase 3+)

### Example API Endpoints

```bash
# Health check
GET http://localhost:5000/api/health

# Authentication (Phase 2)
POST http://localhost:5000/api/auth/register
POST http://localhost:5000/api/auth/login
POST http://localhost:5000/api/auth/refresh

# Inventory (Phase 3)
GET http://localhost:5000/api/products
POST http://localhost:5000/api/products
GET http://localhost:5000/api/products/{id}
PUT http://localhost:5000/api/products/{id}
DELETE http://localhost:5000/api/products/{id}
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

- [x] **Phase 0**: Project Foundation & Setup ✅
- [ ] **Phase 1**: Database Design & Implementation
- [ ] **Phase 2**: Authentication & Authorization Backend
- [ ] **Phase 3**: Inventory Management Backend
- [ ] **Phase 4**: Sales Management Backend
- [ ] **Phase 5**: Purchase Management Backend
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
