# Hiring Intelligence Platform

A lightweight, modular AI-powered backend for candidate-job matching, resume parsing, and hiring analytics. Built with FastAPI, SQLite, Pydantic, and the Google Gemini LLM.

## Quick Start

### 1. Setup Environment

```bash
uv install
uv activate
export GEMINI_API_KEY=test-key  # Use a real Gemini API key for production
```

### 2. Run Development Server

```bash
uv run uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Open interactive API docs: http://127.0.0.1:8000/docs

### 3. Seed Demo Data

```bash
uv run python -c "from backend.cli.seed_demo import seed_demo_data; seed_demo_data()"
```

### 4. Run Tests

```bash
uv run python -m unittest discover -s backend/tests -v
```

## Architecture

The platform is organized into clean layers:

```
backend/
  config/        → Centralized settings (config.py)
  services/      → Core business logic (LLM, parsing, matching, storage)
  repositories/  → Data access (candidates, JDs)
  agents/        → Orchestration layer
    ├─ bulk_agent/       → Batch operations (ranking, parsing, analytics)
    └─ individual_agent/ → Single-entity operations (matching, insights)
  api/           → FastAPI endpoints
  models/        → Pydantic schemas
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Candidate Management
```bash
GET /candidate/all                    # List all candidates
GET /candidate/{email}               # Get candidate by email
POST /upload/resume                  # Upload and parse resume (multipart)
```

### Job Description Management
```bash
POST /job-description/parse          # Parse and save job description
GET /job-description/{job_id}        # Get job description by ID
```

### Matching
```bash
GET /match/candidate/{email}/job/{job_id}  # Score candidate against job
```

## Agents Guide

### Bulk Agents (Batch Operations)

#### RankingAgent
Rank all candidates for a given job using `MatchService` scoring.

```python
from backend.agent.bulk_agent.ranking_agent.agent import RankingAgent
from backend.config.config import AppConfig

config = AppConfig()
agent = RankingAgent()
ranked = agent.rank_candidates_for_job(job_description, db_path=str(config.sqlite_db_path))
# Returns sorted list: [{"candidate_email": "...", "score": 95.0, "details": ...}, ...]
```

#### ResumeParserAgent
Batch parse multiple resumes and save them to the database.

```python
from backend.agent.bulk_agent.resume_parser_agent.agent import ResumeParserAgent
from backend.services.parser_service import ResumeParserService, TextExtractionService
from backend.services.llm_service import LLMService
from backend.services.prompt_loader import PromptLoader

llm = LLMService(config)
parser_svc = ResumeParserService(llm, PromptLoader())
agent = ResumeParserAgent(parser_service=parser_svc)
profiles = agent.parse_and_save(raw_resume_texts, db_path=str(config.sqlite_db_path))
```

#### ScenarioSimulationAgent
Generate candidate variations for testing and scenario analysis.

```python
from backend.agent.bulk_agent.scenario_simulation_agent.agent import ScenarioSimulationAgent

agent = ScenarioSimulationAgent()
variations = agent.simulate_variations(base_candidate_dict, count=5)
```

#### SearchAgent
Simple in-memory search across indexed documents.

```python
from backend.agent.bulk_agent.search_agent.agent import SearchAgent

agent = SearchAgent()
agent.index("candidate_1", "Python FastAPI Docker microservices")
agent.index("candidate_2", "Java Kubernetes Spring Boot")
results = agent.search("Python", top_k=5)
```

#### TalentAnalyticsAgent
Compute aggregate skills distribution and hiring metrics.

```python
from backend.agent.bulk_agent.talent_analytics_agent.agent import TalentAnalyticsAgent

agent = TalentAnalyticsAgent()
skills_dist = agent.skills_distribution(db_path=str(config.sqlite_db_path))
# Returns: {"python": 15, "java": 8, "kubernetes": 12, ...}
```

### Individual Agents (Single-Entity Operations)

#### MatchAgent
Score a single candidate against a single job with optional LLM-enhanced scoring.

```python
from backend.agent.individual_agent.match_agent.agent import MatchAgent
from backend.services.llm_service import LLMService

agent = MatchAgent()
result = agent.match_candidate_to_job("candidate@example.com", job_id=1, db_path=str(config.sqlite_db_path))
# Returns: {"candidate_email": "...", "job_id": 1, "score": 87.5, "details": {...}}

# With LLM (requires valid Gemini API key):
llm_service = LLMService(config)
agent_with_llm = MatchAgent(llm_service=llm_service)
result = agent_with_llm.match_candidate_to_job(..., use_llm=True)
```

#### CandidateProfileAgent
Read and update candidate profiles.

```python
from backend.agent.individual_agent.candidate_profile_agent.agent import CandidateProfileAgent

agent = CandidateProfileAgent()
profile = agent.get("candidate@example.com", db_path=str(config.sqlite_db_path))
new_row_id = agent.save(updated_profile, db_path=str(config.sqlite_db_path))
```

#### CandidateInsightAgent
Generate quick insights for a single candidate.

```python
from backend.agent.individual_agent.candidate_insight_agent.agent import CandidateInsightAgent

agent = CandidateInsightAgent()
insight = agent.skills_summary("candidate@example.com", db_path=str(config.sqlite_db_path))
# Returns: {"skill_count": 5, "skills": ["Python", "Docker", ...]}
```

#### InterviewIntelligenceAgent
Suggest interview questions based on candidate skills.

```python
from backend.agent.individual_agent.interview_intelligence_agent.agent import InterviewIntelligenceAgent

agent = InterviewIntelligenceAgent()
questions = agent.suggest_questions(candidate_profile_dict)
# Returns: ["Tell me about your experience with Python.", ...]
```

## Services

### LLMService
Centralized wrapper for Gemini LLM calls with retry logic and async support.

```python
from backend.services.llm_service import LLMService

service = LLMService(config)
text = service.generate_text(prompt="Summarize this resume: ...")
json_obj = service.generate_json(prompt="...", response_schema=CandidateProfile)
```

### MatchService
Deterministic candidate-job matching with skill, experience, and education scoring.

```python
from backend.services.match_service import MatchService

service = MatchService()
score = service.score_candidate(candidate_profile, job_description)
# Returns: MatchScore(overall=87.5, skill_match=90.0, ...)
```

### ResumeParserService
Parse resumes and job descriptions into validated Pydantic models.

```python
from backend.services.parser_service import ResumeParserService, TextExtractionService

text_extractor = TextExtractionService(config)
parser = ResumeParserService(llm_service, prompt_loader, config)
candidate = parser.parse_resume_text(raw_text)
job = parser.parse_job_description_text(raw_jd_text)
```

### PromptLoader
Load and render YAML prompt templates.

```python
from backend.services.prompt_loader import PromptLoader

loader = PromptLoader()
prompt = loader.load_and_render("path/to/prompt.yaml", "prompt_key", var1="value1")
```

### VectorService (InMemory)
Simple in-memory vector-like store for demo/testing.

```python
from backend.services.vector_service import InMemoryVectorService

vec = InMemoryVectorService()
vec.index("doc_id", "text content", metadata={})
results = vec.search("query", top_k=5)
```

## Configuration

All settings are loaded from environment variables via `AppConfig`:

```bash
GEMINI_API_KEY=sk-...                           # Required: Gemini API key
GEMINI_MODEL=gemini-2.5-flash                   # LLM model (default)
GEMINI_TEMPERATURE=0.0                          # LLM temperature
SQLITE_DB_PATH=backend/data/hiring_platform.db  # Database path
UPLOAD_DIRECTORY=backend/data/resumes           # Resume upload directory
LOG_LEVEL=INFO                                  # Logging level
```

Alternatively, create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-key-here
LOG_LEVEL=DEBUG
```

## Testing

All modules have comprehensive unit tests:

```bash
uv run python -m unittest discover -s backend/tests -v
```

Test coverage includes:
- API endpoints (health, candidates, matching)
- Services (config, storage, LLM, parsing)
- Agents (matching, ranking, analytics, insights)
- Edge cases (candidate not found, invalid jobs, etc.)

**Current: 17 tests, all passing.**

## Development

### Add a New Agent

1. Create a new file in `backend/agent/{bulk,individual}_agent/{agent_name}/agent.py`
2. Inherit from or compose existing services
3. Add unit tests in `backend/tests/test_agents.py`
4. Run: `uv run python -m unittest discover -s backend/tests -v`

### Add a New Service

1. Create a new file in `backend/services/{service_name}.py`
2. Depend on config, logger, and other services
3. Add sync + async methods as needed
4. Test with unit tests

### Add a New API Endpoint

1. Create a new file in `backend/api/{resource}.py`
2. Define FastAPI router with endpoints
3. Register in `backend/app.py`: `app.include_router(router)`
4. Test with `TestClient` in `backend/tests/`

## Known Limitations & Future Work

- **Vector Search**: The `InMemoryVectorService` is a stub. For production, integrate with Pinecone, Weaviate, or Milvus.
- **LLM Caching**: Consider implementing response caching to reduce API costs.
- **Database**: SQLite is fine for local/dev. Migrate to PostgreSQL for production.
- **Frontend**: Add a Streamlit or FastUI dashboard.
- **Orchestration**: Add a chat_orchestrator endpoint that chains multiple agents.
- **Authentication**: Add API key or OAuth2 for production deployments.
- **Docker**: Add Dockerfile and docker-compose for containerized deployment.

## Contact & Support

For questions or issues, open an issue on GitHub or contact the development team.

---

**Last Updated:** 2026-06-21  
**Status:** Active Development  
**License:** MIT
