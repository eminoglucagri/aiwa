# Idea Intake & Feasibility Analysis API

**Document:** IDEA-INTAKE-API v1.0
**Date:** 2026-04-28
**Status:** Initial design
**Related Issue:** AIWA-14

---

## 1. Overview

The idea intake module is the entry point for the AIWA platform. Users submit a natural-language description of a web application they want to build. The system then performs an automated feasibility analysis, evaluating scope, technical complexity, architecture viability, and estimated effort. The result is a structured `AnalysisReport` that feeds into the project creation pipeline.

---

## 2. API Endpoints

### `POST /api/v1/ideas`

Submit a new web application idea for feasibility analysis.

**Request Body:**

```json
{
  "title": "string (required, max 120 chars)",
  "description": "string (required, max 10000 chars)",
  "constraints": {
    "deadline": "string (optional, natural language like '2 weeks')",
    "budget_tier": "enum (free | starter | pro | enterprise, optional)",
    "team_size": "integer (optional, number of developers)",
    "must_haves": ["string (optional list of non-negotiable features)"],
    "nice_to_haves": ["string (optional list of optional features)"]
  },
  "preferences": {
    "tech_stack": ["string (optional, preferred technologies)"],
    "deployment_target": "enum (vercel | cloudflare | railway | self_hosted, optional)",
    "style": "enum (minimal | modern | playful | corporate, optional)"
  }
}
```

**Response (202 Accepted):**

```json
{
  "idea_id": "uuid",
  "status": "analyzing",
  "submitted_at": "ISO8601 timestamp",
  "estimated_completion_seconds": 120
}
```

**Error Responses:**
- `400 Bad Request` — invalid input (missing title/description, description too long)
- `401 Unauthorized` — missing or invalid JWT

---

### `GET /api/v1/ideas/{idea_id}`

Retrieve an idea and its analysis report.

**Response (200 OK):**

```json
{
  "idea_id": "uuid",
  "title": "string",
  "description": "string",
  "status": "analyzing | completed | failed",
  "submitted_at": "ISO8601 timestamp",
  "completed_at": "ISO8601 timestamp | null",
  "analysis": {
    "scope_score": "enum (small | medium | large | xlarge)",
    "complexity_score": "enum (simple | moderate | complex | very_complex)",
    "tech_feasibility": {
      "verdict": "enum (feasible | risky | not_feasible)",
      "challenges": ["string (technical risks or blockers)"],
      "suggestions": ["string (mitigation recommendations)"]
    },
    "estimated_effort_hours": {
      "min": "integer",
      "max": "integer",
      "confidence": "enum (low | medium | high)"
    },
    "recommended_stack": {
      "frontend": "string",
      "backend": "string | null",
      "database": "string | null",
      "deployment": "string"
    },
    "feature_breakdown": [
      {
        "feature": "string",
        "estimated_hours": "integer",
        "priority": "enum (must | should | could)"
      }
    ],
    "risks": [
      {
        "description": "string",
        "severity": "enum (low | medium | high)",
        "mitigation": "string"
      }
    ],
    "summary": "string (2-3 sentence executive summary)"
  }
}
```

**Error Responses:**
- `401 Unauthorized` — missing or invalid JWT
- `404 Not Found` — idea_id does not exist

---

### `GET /api/v1/ideas`

List all ideas for the authenticated user.

**Query Parameters:**
- `status` — filter by `analyzing | completed | failed` (optional)
- `limit` — max results, default 20, max 100 (optional)
- `offset` — pagination offset, default 0 (optional)

**Response (200 OK):**

```json
{
  "ideas": [/* array of idea objects (summary, no analysis detail) */],
  "total": "integer",
  "limit": "integer",
  "offset": "integer"
}
```

---

## 3. Feasibility Analysis Engine

### 3.1 Analysis Pipeline

When `POST /api/v1/ideas` is called:

1. **Idea Creation** — validate input, persist to DB, return `202` with `idea_id`
2. **Async Analysis Trigger** — enqueue a `feasibility_analysis` task to Redis/RQ
3. **Claude Code Analysis** — agent receives the idea payload and executes the analysis prompt
4. **Report Generation** — agent produces structured JSON matching the `AnalysisReport` schema
5. **Persistence** — report saved to DB, `status` updated to `completed`
6. **Notification** — WebSocket/SSE pushed to client (or pollable via `GET`)

### 3.2 Analysis Dimensions

The Claude Code agent evaluates each idea across four dimensions:

| Dimension | Output | Method |
|---|---|---|
| **Scope Score** | `small \| medium \| large \| xlarge` | Feature count × interaction complexity |
| **Complexity Score** | `simple \| moderate \| complex \| very_complex` | Tech stack breadth × integration requirements |
| **Tech Feasibility** | `feasible \| risky \| not_feasible` + challenges/suggestions | Architecture review against available tools (Claude Code, Vercel, NeonDB) |
| **Effort Estimation** | `{min, max}` hours + confidence | Historical data pattern matching + agent judgment |

### 3.3 Analysis Prompt Structure

```
You are a senior web development architect analyzing a project idea.

## Project Idea
Title: {title}
Description: {description}
Constraints: {constraints JSON}
Preferences: {preferences JSON}

## Your Task
Evaluate this idea across four dimensions and produce a structured analysis report.

## Constraints for Analysis
- Deployment target: Vercel (primary)
- Database options: NeonDB (PostgreSQL), no external DB required
- AI runtime: Claude Code CLI (available tools: file creation, git, npm, etc.)
- Tech stack flexibility: any modern web stack (React, Vue, Svelte, Next.js, etc.)
- Do NOT assume external APIs beyond standard web APIs

## Output Format
Return a JSON object with this exact structure:
{
  "scope_score": "small|medium|large|xlarge",
  "complexity_score": "simple|moderate|complex|very_complex",
  "tech_feasibility": {
    "verdict": "feasible|risky|not_feasible",
    "challenges": ["challenge1", ...],
    "suggestions": ["suggestion1", ...]
  },
  "estimated_effort_hours": {
    "min": number,
    "max": number,
    "confidence": "low|medium|high"
  },
  "recommended_stack": {
    "frontend": "string",
    "backend": "string|null",
    "database": "string|null",
    "deployment": "string"
  },
  "feature_breakdown": [
    {
      "feature": "string",
      "estimated_hours": number,
      "priority": "must|should|could"
    }
  ],
  "risks": [
    {
      "description": "string",
      "severity": "low|medium|high",
      "mitigation": "string"
    }
  ],
  "summary": "string (2-3 sentence executive summary)"
}

## Guidelines
- Be conservative with effort estimates — add 20% buffer for edge cases
- Flag any features that require external services not supported by Vercel/NeonDB
- If the idea is not feasible, explain why and suggest a minimal viable alternative
- "risky" verdict means achievable with additional care/mitigation
```

---

## 4. Database Schema

### `ideas` Table

```sql
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    constraints JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'analyzing',
    analysis JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_ideas_user_id ON ideas(user_id);
CREATE INDEX idx_ideas_status ON ideas(status);
```

---

## 5. Webhook / SSE (Optional Enhancement)

When analysis completes, the server can push a notification via WebSocket:

**Channel:** `user:{user_id}:ideas`

**Payload:**
```json
{
  "event": "idea_completed",
  "idea_id": "uuid",
  "title": "string"
}
```

Clients can subscribe instead of polling `GET /api/v1/ideas/{idea_id}`.

---

## 6. Error Handling

| Scenario | HTTP Status | Response Body |
|---|---|---|
| Missing title | `400` | `{"detail": "title is required"}` |
| Missing description | `400` | `{"detail": "description is required"}` |
| Description > 10000 chars | `400` | `{"detail": "description must be 10000 characters or fewer"}` |
| Idea not found | `404` | `{"detail": "idea not found"}` |
| Analysis fails | `200` (status=failed) | Idea record has `status=failed`, analysis contains error |
| Auth failure | `401` | `{"detail": "Not authenticated"}` |

---

## 7. Security Considerations

- All endpoints require JWT authentication
- Ideas are scoped to the authenticated user (user_id filter on all queries)
- No PII stored in idea descriptions (user responsible for content)
- Rate limiting: 10 idea submissions per user per hour
- Analysis prompts do not include user credentials or internal system details

---

## 8. File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── ideas.py     # /api/v1/ideas endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings, env vars
│   │   └── security.py      # JWT validation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py      # DB connection
│   │   └── models.py        # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── ideas.py         # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── feasibility.py   # Claude Code analysis integration
├── tests/
│   ├── __init__.py
│   ├── test_ideas_api.py
│   └── test_feasibility.py
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   └── IdeaIntake/
│   │       ├── IdeaForm.tsx
│   │       └── AnalysisReport.tsx
│   └── pages/
│       └── NewIdea.tsx
```

---

## 9. Dependencies

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
anthropic>=0.18.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.9
httpx>=0.27.0
rq>=1.16.0
redis>=5.0.0
```

---

## 10. Open Questions

| Question | Status | Notes |
|---|---|---|
| Should analysis be synchronous or async? | **Async** | Long-running LLM calls mean async is better; return 202 with polling |
| Store full analysis JSON in DB or parse into columns? | **JSONB** | Flexibility for future fields; parsed at read time |
| Support anonymous idea submission? | **No** | All ideas require authenticated user context |
| SLA for analysis completion? | **120s target** | Claude Code analysis should complete within 2 minutes |