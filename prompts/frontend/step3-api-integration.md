# Step 3: API Integration

You are wiring up API integration points for the frontend. Components are scaffolded, now connect them to the Control Plane API.

## API Base URL

{api_base_url}

## Feature Specs

{insert validated feature list here}

## API Boundaries (from Architecture)
- POST /auth/register, POST /auth/login, POST /auth/refresh
- GET /projects, POST /projects, GET /projects/{id}, DELETE /projects/{id}
- POST /projects/{id}/generate
- GET /projects/{id}/tasks, GET /tasks/{id}
- POST /projects/{id}/deploy
- GET /projects/{id}/logs (SSE)

## Instructions

1. Create `src/lib/api.ts` — typed API client:
   ```typescript
   // Base axios instance with interceptors
   // Auth token injection (from httpOnly cookie or localStorage)
   // Response interceptor for error handling
   // Typed endpoints matching the API spec
   ```
2. Create `src/types/api.ts` — TypeScript interfaces for all API request/response types
3. Create `src/hooks/` — React Query hooks:
   - `useAuth` — login, register, refresh, logout
   - `useProjects` — list, create, delete
   - `useProject(id)` — fetch single project
   - `useGenerate` — submit generation request
   - `useDeploy` — trigger deployment
   - `useTaskLogs` — SSE log streaming
4. Authentication:
   - JWT stored in httpOnly cookie (preferred) or localStorage
   - Auth middleware on routes requiring login
   - Redirect to /login when unauthenticated
5. Error handling:
   - API errors mapped to user-friendly messages
   - Toast notifications for success/error feedback
   - Retry logic for transient failures (3 retries, exponential backoff)
6. SSE for log streaming:
   - `useEventSource` hook or native EventSource
   - Reconnect on disconnect
   - Buffer and display log lines
7. Update components to use the React Query hooks instead of local state
8. Commit and push

Respond with a summary of API integration wired up.
