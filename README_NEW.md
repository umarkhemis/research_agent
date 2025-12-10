# 🔬 ResearchHub Pro - Full Stack Version

A modern, full-stack AI-powered academic research assistant built with Django REST Framework and React.

## 🏗️ Architecture

### Backend (Django REST Framework)
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (with SQLite fallback for development)
- **AI Integration**: Groq LLM for summarization and analysis
- **APIs**: Semantic Scholar + ArXiv for paper search
- **Features**:
  - RESTful API endpoints
  - Paper search and management
  - AI-powered summarization
  - Literature review generation
  - Multi-format export (PDF, Word, LaTeX, BibTeX)
  - Project organization

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Routing**: React Router v6
- **UI Features**:
  - Dark/Light mode
  - Responsive design
  - Modern gradient theme (Indigo/Purple)
  - Toast notifications
  - Loading states

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (optional, SQLite works for development)
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repo-url>
cd research_agent
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start with Docker Compose**
```bash
docker-compose up --build
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp ../.env.example ../.env
# Edit .env with your API keys
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Backend will be available at http://localhost:8000

#### Frontend Setup

1. **Navigate to frontend** (in a new terminal)
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit if needed (default points to localhost:8000)
```

4. **Run development server**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

## 🔑 API Keys

### Groq API (Required - FREE)
1. Go to https://console.groq.com/keys
2. Sign up (takes 30 seconds)
3. Create an API key
4. Add to `.env` as `GROQ_API_KEY`

### Semantic Scholar API (Optional)
1. Go to https://www.semanticscholar.org/product/api
2. Request an API key (increases rate limits)
3. Add to `.env` as `SEMANTIC_SCHOLAR_API_KEY`

## 📁 Project Structure

```
research_agent/
├── backend/                  # Django backend
│   ├── api/                 # Django app
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # API views
│   │   └── urls.py         # API routes
│   ├── services/           # Business logic
│   │   ├── search_service.py
│   │   ├── pdf_service.py
│   │   ├── llm_service.py
│   │   ├── literature_review_service.py
│   │   ├── export_service.py
│   │   └── cache_service.py
│   ├── utils/              # Utilities
│   ├── research_agent/     # Django project settings
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   │   ├── common/   # Reusable components
│   │   │   ├── layout/   # Layout components
│   │   │   ├── papers/   # Paper components
│   │   │   ├── projects/ # Project components
│   │   │   └── literature-review/
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── store/        # State management
│   │   └── utils/        # Utilities
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔌 API Endpoints

### Papers
- `POST /api/papers/search/` - Search papers
- `GET /api/papers/` - List papers
- `GET /api/papers/{id}/` - Get paper details
- `POST /api/papers/{id}/summarize/` - Generate summary
- `POST /api/papers/{id}/analyze/` - Extract gaps & findings
- `POST /api/papers/{id}/download_pdf/` - Download PDF

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project
- `POST /api/projects/{id}/add_paper/` - Add paper to project
- `DELETE /api/projects/{id}/papers/{paper_id}/` - Remove paper
- `GET /api/projects/{id}/papers/` - Get project papers

### Literature Reviews
- `POST /api/literature-reviews/generate/` - Generate review
- `GET /api/literature-reviews/{id}/` - Get review
- `GET /api/literature-reviews/` - List reviews

### Export
- `POST /api/export/papers/` - Export papers
- `POST /api/export/review/` - Export review

### Statistics
- `GET /api/statistics/dashboard/` - Dashboard stats

## 🎨 Features

### Core Functionality
- ✅ Multi-database paper search (Semantic Scholar + ArXiv)
- ✅ AI-powered paper summarization (3 detail levels)
- ✅ Research gap identification
- ✅ Key findings extraction
- ✅ Project organization
- ✅ Literature review generation
- ✅ Multi-format export
- ✅ Search history
- ✅ Caching system

### UI/UX
- ✅ Modern gradient theme (Indigo/Purple)
- ✅ Dark/Light mode toggle
- ✅ Responsive design
- ✅ Smooth animations
- ✅ Loading states
- ✅ Toast notifications
- ✅ Modal dialogs

## 🧪 Development

### Backend Testing
```bash
cd backend
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### Linting
```bash
# Backend
cd backend
flake8

# Frontend
cd frontend
npm run lint
```

## 🚢 Deployment

### Environment Variables for Production
Make sure to set these in your production environment:
- `SECRET_KEY` - Strong Django secret key
- `DEBUG=False`
- `ALLOWED_HOSTS` - Your domain
- `DATABASE_URL` - PostgreSQL connection string
- `GROQ_API_KEY`
- `SEMANTIC_SCHOLAR_API_KEY`

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📧 Support

For issues and questions, please open a GitHub issue.
