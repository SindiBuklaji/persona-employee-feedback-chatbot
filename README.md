# persona-employee-feedback-chatbot

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Setup
1. Create `backend/.env` with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

2. Start all services:
   ```bash
   docker-compose up
   ```

### Access
- **Frontend**: http://localhost:8501 (Streamlit)
- **Backend API**: http://localhost:8000 (FastAPI)
- **Database**: PostgreSQL on port 5432

## Project Overview
Research study evaluating how AI chatbot personas (warm vs. competent) affect psychological safety and feedback quality in workplace scenarios.