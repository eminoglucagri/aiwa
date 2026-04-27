# System Architecture — AI Web Development Automation Platform

**Document:** AIWA Architecture v1.0
**Date:** 2026-04-27
**Status:** Initial design

---

## 1. System Overview

The platform orchestrates AI agents to generate, test, and deploy web applications from natural-language specifications. A user submits a project idea through the Web UI; the Control Plane coordinates one or more Agent Runtimes that produce a complete, deployable web application.

The architecture follows a **control plane + worker** pattern: the Control Plane owns all state, scheduling, and external integrations; Agent Runtimes are stateless workers that receive tasks, execute them in isolated sandboxes, and report results.

---

## 2. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Web UI** | React 18 + TypeScript, Vite, Tailwind CSS | Fast iteration, strong TypeScript ecosystem, existing AI tooling integration |
| **Web Server / API** | Python FastAPI | Async-native, strong LLM/library ecosystem (anthropic, httpx, gitpython), rapid development |
| **Database** | PostgreSQL 16 | ACID transactions for task state; JSONB for flexible task payload storage; row-level security for multi-tenant isolation |
| **Task Queue** | Redis + RQ (or Celery) | Lightweight, Redis already required for session/cache; RQ is simpler than Celery for this scale |
| **Agent Runtime** | Claude Code CLI + Claude API (Anthropic) | Claude Code provides built-in tool-use, sandboxed execution, and file operations; Minimax M2.7 as fallback model |
| **Code Storage** | Git repositories (per-project) + S3-compatible object storage for artifacts | Git gives versioning and PR workflows; S3 for build artifacts, logs, and generated media |
| **Sandbox** | Docker containers (gVisor optional for future hardening) | Agent processes run inside ephemeral containers with no host access; network egress restricted |
| **Deployment Target** | Vercel API + GitHub integration | Vercel provides zero-config deployment; GitHub as the canonical repo host |
| **Auth** | JWT (access + refresh tokens) | Stateless, widely understood; refresh tokens enable short-lived sessions |
| **Infrastructure** | Docker Compose (dev) → Kubernetes (prod) | Local development parity; horizontal scaling for agent workers in production |
| **Monitoring** | Prometheus + Grafana | Standard observability; agent execution metrics critical for tuning |

---

## 3. Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User's Browser                         │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Web UI (React SPA)                      │
│          Serves static assets; talks to API only            │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST / WebSocket
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Control Plane API (FastAPI)               │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │  Auth    │  │  Project │  │  Task    │  │  Webhook    │  │
│  │  Service │  │  Service │  │  Queue   │  │  Handler    │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              PostgreSQL (state + metadata)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Redis (sessions, queue, cache)          │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────┬───────────────────────┬──┘
           │                      │                       │
           │ Task dispatch        │ Artifact push         │ Webhook/event
           ▼                      ▼                       ▼
┌──────────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│  Agent Worker 1      │  │  Git Server       │  │  Vercel / GitHub  │
│  (Docker container)  │  │  (Git repos)      │  │  (deployment)     │
│  Claude Code runtime │  │  Per-project Git │  │                   │
├──────────────────────┤  └───────────────────┘  └──────────────────┘
│  Agent Worker N      │
│  (Docker container)  │
│  Claude Code runtime │
└──────────────────────┘
```

### 3.1 Components

#### Web UI
- Single-page application served as static assets (CDN-friendly)
- Communicates exclusively via REST API for data and WebSocket for real-time task updates
- No direct database or agent access
- Stores JWT in httpOnly cookie; refresh token managed by API

#### Control Plane API (FastAPI)
- Central authority for all state and coordination
- Owns the PostgreSQL schema and Redis data structures
- Exposes REST endpoints for project CRUD, task submission, status queries
- Pushes task results via WebSocket or SSE
- Manages authentication: issues JWTs, validates tokens, enforces RBAC
- All external integrations (GitHub, Vercel) are accessed server-side only — agents and clients never hold external service credentials

#### Agent Workers
- Stateless, horizontally scalable
- Each worker runs inside an ephemeral Docker container
- Receives task payload via Redis queue
- Executes Claude Code with project-specific context and tool permissions
- Writes generated code to project Git repository
- Reports completion/failure back to Control Plane API
- No two agents share a container; each task gets a fresh environment

#### PostgreSQL Schema (conceptual)

```
users           — id, email, password_hash, mfa_secret, role, created_at
projects        — id, user_id, name, description, github_repo_id, vercel_project_id, status, created_at
tasks           — id, project_id, type (generate|test|deploy), status, payload (JSONB), result (JSONB), created_at, completed_at
audit_log       — id, actor_id, action, resource, metadata (JSONB), created_at
agent_sessions  — id, worker_id, task_id, started_at, ended_at
```

#### Redis Structures
- **Queue**: `rq:tasks` — pending task queue with priority
- **Cache**: `project:{id}:status` — cached project status (TTL 30s)
- **Sessions**: `session:{token}` — short-lived agent session tokens

### 3.2 Code Storage Layout

```
/repos/{project_id}/
  ├── .git/
  ├── src/              — generated application source
  ├── tests/            — generated test suite
  ├── package.json
  ├── vercel.json       — Vercel deployment config
  └── README.md
```

Each project maps to one Git repository. Agents clone, write, commit, and push. The Control Plane manages GitHub integration server-side.

---

## 4. Data Flow

### 4.1 Project Creation Flow

```
1. User submits project spec via Web UI (POST /projects)
2. Control Plane creates DB record (status=initializing)
3. Control Plane initializes GitHub repo (server-side OAuth token)
4. Control Plane enqueues a "bootstrap" task
5. Agent Worker picks up task:
   a. Clones the (empty) repo
   b. Sets up project scaffold (package.json, vercel.json, etc.)
   c. Commits and pushes
6. Agent reports completion → Control Plane updates project status=ready
7. Web UI reflects "Project ready" via WebSocket
```

### 4.2 Code Generation Flow

```
1. User submits generation request via Web UI (POST /projects/{id}/generate)
2. Control Plane enqueues a "generate" task with full context:
   - Project ID, user intent, existing file tree, tech stack preferences
   - Agent credentials (scoped GitHub token, Vercel deploy token)
3. Agent Worker picks up task:
   a. Claude Code receives the prompt + tool permissions
   b. Agent reads existing files, generates new ones
   c. Agent runs tests (npm test / pytest)
   d. Agent commits and pushes changes
   e. Agent calls Control Plane webhook to report result
4. Control Plane updates task status + project status
5. Web UI receives update via WebSocket
```

### 4.3 Deployment Flow

```
1. User triggers deployment via Web UI (POST /projects/{id}/deploy)
2. Control Plane verifies project is in deployable state
3. Control Plane calls Vercel API to trigger a new deployment
   - Uses server-side Vercel OAuth token
4. Vercel notifies Control Plane via webhook on deploy status
5. Control Plane updates project status and notifies Web UI
```

---

## 5. API Boundaries

### 5.1 Public API (Web UI → Control Plane)

All endpoints require JWT authentication unless noted.

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/login` | Login, returns JWT |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/projects` | List user's projects |
| `POST` | `/projects` | Create a new project |
| `GET` | `/projects/{id}` | Get project details |
| `DELETE` | `/projects/{id}` | Delete project |
| `POST` | `/projects/{id}/generate` | Submit generation request |
| `GET` | `/projects/{id}/tasks` | List tasks for a project |
| `GET` | `/tasks/{id}` | Get task details |
| `POST` | `/projects/{id}/deploy` | Trigger deployment |
| `GET` | `/projects/{id}/logs` | Stream task logs (SSE) |

### 5.2 Internal API (Agent → Control Plane)

Agents call these endpoints using scoped session tokens (not user JWTs).

| Method | Path | Description |
|---|---|---|
| `POST` | `/agent/task/{id}/heartbeat` | Periodic liveness + progress update |
| `POST` | `/agent/task/{id}/complete` | Report task completion with results |
| `POST` | `/agent/task/{id}/fail` | Report task failure with error details |
| `GET` | `/agent/task/{id}/context` | Fetch full task context (files, config) |
| `POST` | `/agent/project/{id}/upload-artifact` | Upload generated files |

### 5.3 Webhook API (External → Control Plane)

| Method | Path | Source | Description |
|---|---|---|---|
| `POST` | `/webhooks/vercel` | Vercel | Deployment status updates |
| `POST` | `/webhooks/github` | GitHub | Repo events (push, PR) |

---

## 6. Deployment Model

### 6.1 Environments

| Environment | Scope | Deployment |
|---|---|---|
| **Local Dev** | Single developer | Docker Compose (API + DB + Redis + 1 agent worker) |
| **Staging** | Integration testing | Kubernetes on cloud (2x API replicas, 4x agent workers, managed DB) |
| **Production** | Live users | Kubernetes on cloud, multi-AZ, horizontal scaling |

### 6.2 Container Images

| Image | Base | Description |
|---|---|---|
| `aiwa-api` | Python 3.12-slim | FastAPI application |
| `aiwa-worker` | Python 3.12-slim + Claude Code | Agent worker process |
| `aiwa-sandbox` | gVisor + minimal distro | Hardened container image for agent execution |

### 6.3 Scaling Strategy

- **API servers**: Horizontal scaling behind load balancer; stateless, no sticky sessions
- **Agent workers**: Kubernetes HPA based on Redis queue depth; scale-to-zero when idle
- **Database**: Managed PostgreSQL (e.g., Neon, RDS) with connection pooling (PgBouncer)
- **Redis**: Managed Redis (e.g., Upstash) with replication

### 6.4 Secrets Management

All secrets (JWT signing key, DB credentials, Vercel token, GitHub token) stored in environment variables injected at runtime via Kubernetes secrets or a secrets manager (HashiCorp Vault / AWS Secrets Manager). No secrets in code or configuration files.

---

## 7. Security Architecture

Derived from the threat model. Key decisions:

| Concern | Approach |
|---|---|
| Agent isolation | Ephemeral Docker containers per task; no host filesystem/network access |
| Credential scoping | Agents receive short-lived, scoped tokens per task; never persistent secrets |
| Multi-tenant isolation | PostgreSQL row-level security; agent filesystem restricted to project directory |
| Audit trail | All state-changing operations logged to `audit_log` table with actor identity |
| Secret injection prevention | Pre-commit hooks scan for credentials; logs redact sensitive fields |
| Agent tool injection | Tool permissions scoped per task type; all tool calls logged and auditable |

---

## 8. Key Design Decisions & Trade-offs

1. **Python FastAPI over Node.js**: Python has a richer ecosystem for AI integrations (Anthropic SDK, gitpython, subprocess management). TypeScript could have been used for a unified stack but Python's async I/O matches FastAPI's model well.

2. **PostgreSQL over NoSQL**: Task payloads are JSONB but the relational model fits projects, users, and audit logs naturally. Multi-tenant RBAC benefits from foreign key constraints.

3. **Redis queue over a message broker**: RQ is simple and Python-native. At early scale, this avoids the operational complexity of Kafka or RabbitMQ. Can be swapped if throughput demands.

4. **Git-native code storage**: Storing generated code in Git (per project) gives versioning, diffs, and PR workflows for free. Agents use the Git CLI — no custom storage layer needed.

5. **Agents as ephemeral workers, not long-lived services**: Stateless workers are easier to scale and audit. Each task gets a fresh container — no cross-task state leakage.

6. **Sandbox-first over VM-based isolation**: Docker containers are faster to provision than VMs. If gVisor hardening proves insufficient, migrate to microVMs (Firecracker) in a later phase.

7. **Server-side external integrations**: All OAuth flows (GitHub, Vercel) are handled by the Control Plane. Agents receive scoped, short-lived tokens. This prevents token leakage through agent prompts or logs.

---

## 9. Open Questions

| Question | Status | Notes |
|---|---|---|
| Claude Code CLI availability on Linux | Open | Verify Claude Code supports headless Linux environments and containerized execution |
| Minimax M2.7 API integration path | Open | Determine if Minimax provides a Claude-compatible API or requires a separate adapter |
| Vercel team vs. personal accounts | Open | Decide multi-tenant deployment model (one Vercel org per platform user vs. shared) |
| Agent task timeout policy | Open | Default timeout per task type; escalation path for long-running generation |
| Database migration strategy | Open | Alembic for schema migrations; CI gate before production applies migrations |
| CI/CD for the platform itself | Open | Not required for initial release; plan for GitHub Actions pipeline post-MVP |
