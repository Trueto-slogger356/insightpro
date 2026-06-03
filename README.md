# InsightPro

AI-powered customer experience and insights platform. This repository contains Phase 1 and Phase 2 implementation slices.

## Phase 1 Scope

- Admin login with JWT-compatible token flow
- Survey creation with text, radio, checkbox, dropdown, rating, and NPS questions
- Publish surveys with a unique public URL
- Respondent survey experience with step-by-step save
- Branching logic: route to a target question when an answer matches
- Resume incomplete responses through Redis-backed progress sessions
- Final submissions stored in PostgreSQL
- Basic admin dashboard with response list and CSV export
- S3-ready upload/export service abstraction for later assets and reports

## Phase 2 Scope

- Multi-tenant company/customer model with tenant-scoped users, surveys, responses, invites, and audit logs
- Role-based access control for `super_admin`, `customer_admin`, and `analyst`
- Custom branding with tenant/survey logo URL, primary color, and theme metadata
- Custom survey URLs through `/survey/{custom_url}`
- Anonymous and identified response modes
- Advanced logic fields for branching, display conditions, and scoring rules
- Analytics endpoint with filters for country, product, service, region, date-ready schema fields, average score, and chart buckets
- CSV, Excel-compatible XML, and HTML report exports
- Email invite queue model and invite API, ready for async provider integration
- Audit logging for tenant, user, survey, publishing, and invite operations
- Existing database startup patches for Phase 1 Docker volumes
- GitLab CI, Jenkinsfile, AWS ECS task skeleton, Terraform starter files

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, JWT/OAuth2, async-ready services
- Frontend: React, Vite
- Local services: Docker Compose for API, PostgreSQL, Redis, and frontend

## Run Locally

```bash
cp .env.example .env
docker compose up --build
```

Frontend: http://localhost:5173

Backend docs: http://localhost:8000/docs

Seed admin:

- Email: `admin@insightpro.local`
- Password: `admin123`

## API Modules

- `auth`: login, password hashing, JWT token helpers
- `tenants`: tenant management, branding, users, audit logs
- `surveys`: survey builder, question manager, publishing, custom URLs, CSV/Excel/PDF exports
- `responses`: public survey flow, progress save/resume, final submission
- `dashboard`: tenant-aware summary and filtered analytics
- `notifications`: email invite queue and invite URL generation
- `logic_engine`: branching, display-condition helpers, and score calculation
- `resume_session`: Redis-backed incomplete survey state

## Frontend Flows

- Admin workspace: create branded tenant-aware surveys, publish links, inspect responses, filter analytics, export CSV/Excel/PDF, queue invites
- Public survey runner: answer questions one at a time, capture identified respondent email when needed, resume progress, submit

## Local Checks

```bash
./scripts/run_checks.sh
```

## Deployment Scaffolding

- GitLab: `.gitlab-ci.yml`
- Jenkins: `Jenkinsfile`
- ECS: `infra/ecs/task-definition.json`
- Terraform: `infra/terraform`

## Next Phase

Phase 3 is for AI Insights + Scale + Full Production; so will add AI insight generation, sentiment analysis, trend detection, RAG-based Q&A, event processing, monitoring, and production-grade security hardening.

Goal: make it smart, scalable, and enterprise-grade.

Features to add :

AI-generated survey summaries
Sentiment analysis
Theme/topic extraction from text answers
Risk indicators
Trend comparison across surveys
Question-level insights
Auto-generated executive summary
RAG-based Q&A on survey responses
Benchmarking reports
Large scale response handling
High availability deployment
Monitoring and alerting
Security hardening
GDPR/data retention support

Tech

OpenAI API
LangChain
RAG pipelines
PostgreSQL + vector search or separate vector DB if needed
Redis for caching AI results
Kafka for event-driven processing
Docker + ECS/Kubernetes
Terraform infrastructure
CloudWatch/Prometheus/Grafana
Bash/Python scripts for automation

Main modules

AI insight engine
Sentiment analysis pipeline
RAG Q&A module
Event processing with Kafka
Scalable analytics service
Monitoring and observability
Security/compliance layer
Production deployment automation


## Current Structure

```
├── insightpro/                         # Root project folder for the customer survey insights platform
│   ├── README.md                       # Project overview, setup steps, architecture notes, and usage guide
│   ├── .env                            # Local environment variables for backend, database, Redis, S3, auth, etc.
│   ├── .env.example                    # Sample environment file showing required config keys
│   ├── Jenkinsfile                     # Jenkins CI/CD pipeline definition for build, test, and deployment
│   ├── docker-compose.yml              # Local development setup for frontend, backend, Postgres, Redis, etc.
│   ├── .gitlab-ci.yml                  # GitLab CI/CD pipeline for automated build, test, and deployment
│   ├── .gitlab/                        # GitLab-specific configuration folder

│   ├── infra/                          # Infrastructure-as-code and cloud deployment configuration
│   │   ├── terraform/                  # Terraform files for provisioning AWS/cloud infrastructure
│   │   │   ├── main.tf                 # Main Terraform resources like ECS, networking, S3, RDS, Redis, IAM
│   │   │   └── variables.tf            # Terraform input variables for environment-specific configuration
│   │   ├── ecs/                        # ECS deployment configuration
│   │   │   └── task-definition.json    # ECS task definition for running backend/frontend containers

│   ├── frontend/                       # React frontend application for admin dashboard and survey UI
│   │   ├── index.html                  # Main HTML entry point for the React app
│   │   ├── Dockerfile                  # Docker image definition for building and serving frontend
│   │   ├── package.json                # Frontend dependencies, scripts, and project metadata
│   │   ├── package-lock.json           # Locked npm dependency versions
│   │   ├── dist/                       # Production build output folder
│   │   │   ├── index.html              # Built HTML file for production deployment
│   │   │   ├── assets/                 # Compiled frontend JS and CSS assets
│   │   │   │   ├── index-DF6AwFyC.js   # Bundled production JavaScript file
│   │   │   │   └── index-B3cCsnnh.css  # Bundled production CSS file
│   │   ├── src/                        # React source code folder
│   │   │   ├── main.jsx                # Main React entry file where the app is mounted
│   │   │   ├── styles/                 # Frontend styling folder
│   │   │   │   └── app.css             # Global CSS styles for dashboard and survey screens
│   │   │   ├── components/             # Reusable React UI components
│   │   │   ├── api/                    # Frontend API integration layer
│   │   │   │   └── client.js           # Axios/fetch client for calling backend APIs

│   ├── backend/                        # FastAPI backend application
│   │   ├── requirements.txt            # Python backend dependencies
│   │   ├── Dockerfile                  # Docker image definition for backend service
│   │   ├── app/                        # Main backend application package
│   │   │   ├── main.py                 # FastAPI app startup, middleware, and router registration
│   │   │   ├── core/                   # Core configuration and security utilities
│   │   │   │   ├── config.py           # App settings loaded from environment variables
│   │   │   │   └── security.py         # JWT, OAuth2, password hashing, and auth helpers
│   │   │   ├── models/                 # SQLAlchemy database models
│   │   │   │   ├── survey.py           # Survey, question, option, and logic-related DB models
│   │   │   │   ├── user.py             # User and role-related DB models
│   │   │   │   ├── tenant.py           # Customer/tenant organization DB model
│   │   │   │   └── response.py         # Survey response and answer DB models
│   │   │   ├── schemas/                # Pydantic request and response schemas
│   │   │   │   ├── auth.py             # Login, token, and authentication schemas
│   │   │   │   ├── survey.py           # Survey creation, update, question, and logic schemas
│   │   │   │   ├── tenant.py           # Tenant/customer request and response schemas
│   │   │   │   ├── notification.py     # Email invite and reminder schemas
│   │   │   │   └── response.py         # Survey response submission and resume schemas
│   │   │   ├── db/                     # Database setup and schema utilities
│   │   │   │   ├── session.py          # PostgreSQL database session and connection setup
│   │   │   │   ├── base.py             # Base SQLAlchemy metadata/model registration
│   │   │   │   └── schema.py           # DB initialization or schema helper logic
│   │   │   ├── api/                    # FastAPI route handlers
│   │   │   │   ├── auth.py             # Login, signup, token refresh, and auth APIs
│   │   │   │   ├── public.py           # Public survey access and response submission APIs
│   │   │   │   ├── deps.py             # Common route dependencies like current user and DB session
│   │   │   │   ├── surveys.py          # Survey builder, publish, update, and management APIs
│   │   │   │   ├── dashboard.py        # Dashboard metrics, charts, and analytics APIs
│   │   │   │   ├── notifications.py    # Survey invite and reminder APIs
│   │   │   │   └── tenants.py          # Tenant/customer setup and management APIs
│   │   │   ├── services/               # Business logic layer
│   │   │   │   ├── logic_engine.py     # Branching, skip logic, conditional flow, and next-question logic
│   │   │   │   ├── notification_service.py # Email invitation and reminder processing logic
│   │   │   │   ├── resume_session.py   # Redis-based incomplete survey progress and resume handling
│   │   │   │   ├── export_service.py   # CSV, Excel, or report export generation logic
│   │   │   │   ├── audit_service.py    # Audit trail logging for admin and system actions
│   │   │   │   ├── permissions.py      # RBAC, tenant-level access checks, and authorization rules
│   │   │   │   └── storage_service.py  # S3 upload/download handling for assets, reports, and exports
│   │   └── tests/                      # Backend test cases for APIs, services, and business logic

│   ├── scripts/                        # Utility scripts for local checks and automation
│   │   └── run_checks.sh               # Script to run linting, tests, formatting, or basic health checks

```
