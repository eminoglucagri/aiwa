# Backend API Generator — Claude Code Prompt Chain
## AIWA-18 | Production-Ready Node.js/Express Backend Generator

**Status:** Draft v1.0
**Date:** 2026-04-28
**Scope:** Given validated features and data models → production-ready Node.js/Express backend

---

## Overview

This prompt chain is invoked by a Claude Code agent worker once a project has validated feature specs and data models. The chain runs in four sequential steps:

1. **Scaffold** — Bootstrap Express project structure
2. **Endpoints** — Implement REST routes with error handling
3. **Middleware** — Add validation + auth middleware
4. **Business Logic** — Implement service layer per feature specs

Output is a deployable Node.js/Express project with OpenAPI documentation.

---

## Invoker Context

The Control Plane passes this context to the agent worker at task dispatch:

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "features": [ ... validated feature specs ... ],
  "data_models": [ ... validated data models ... ],
  "auth_type": "jwt" | "api-key",
  "db_connection": "<connection-string or null>",
  "deployment_target": "vercel"
}
```

---

## Step 1: Scaffold

### Prompt

```
You are building the backend API for a new project. Your task is to scaffold a production-ready Node.js/Express project.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Auth type: {auth_type}
- Database: {db_connection}

## Feature Summary
{insert validated feature specs here}

## Data Models
{insert validated data models here}

## Instructions
1. Clone the repo at {repo_url}
2. Create the following directory structure under `backend/`:
   backend/
   ├── src/
   │   ├── routes/          # Express routers
   │   ├── controllers/     # Request handlers
   │   ├── services/        # Business logic
   │   ├── middleware/      # Auth, validation, error handling
   │   ├── models/          # Data models / ORM schemas
   │   ├── utils/           # Helpers
   │   └── app.js           # Express app setup
   ├── tests/
   │   ├── unit/
   │   └── integration/
   ├── package.json
   ├── .env.example
   └── vercel.json          # Vercel serverless config
3. Initialize package.json with these dependencies:
   - express, cors, helmet, compression
   - jsonwebtoken, bcryptjs
   - joi or zod (validation)
   - prisma or sequelize (ORM)
   - swagger-ui-express, swagger-jsdoc (API docs)
   - jest, supertest (testing)
   - dotenv
4. Create a base Express app in src/app.js with:
   - CORS, Helmet, compression middleware
   - JSON body parser
   - Swagger UI at /api/docs
   - 404 handler and global error handler
   - Health check endpoint at GET /health
5. Create .env.example with all required env vars:
   - PORT, NODE_ENV
   - DATABASE_URL
   - JWT_SECRET, JWT_EXPIRES_IN
   - (deployment-specific vars)
6. Create vercel.json for serverless Express deployment
7. Create a README.md section in the repo's README covering:
   - Setup instructions
   - Environment variables
   - How to run locally
   - API documentation link
8. Commit and push

Respond with a summary of what was created.
```

### Deliverable
- `backend/` directory with project skeleton committed and pushed

---

## Step 2: REST Endpoints

### Prompt

```
You are implementing REST endpoints for the backend API. Using the scaffolded project structure, implement all endpoints defined in the feature specs.

## Feature Specs
{insert validated feature specs here}

## Data Models
{insert validated data models here}

## Instructions
1. For each feature, create a route file under src/routes/ named after the resource (e.g., users.js, projects.js)
2. Each route file should use an Express Router
3. For each endpoint, create a corresponding controller in src/controllers/
4. Controllers must:
   - Extract and validate request parameters (params, query, body)
   - Call the appropriate service method
   - Return JSON responses with proper HTTP status codes
   - Wrap all logic in try/catch and call next(err) on failure
5. HTTP status code conventions:
   - GET: 200 OK, 404 Not Found
   - POST: 201 Created, 400 Bad Request, 401 Unauthorized
   - PUT/PATCH: 200 OK, 400 Bad Request, 404 Not Found
   - DELETE: 204 No Content, 404 Not Found
6. Error responses must follow this format:
   { "error": { "code": "RESOURCE_NOT_FOUND", "message": "Human readable message" } }
7. Register all routers in src/app.js
8. Add Swagger JSdoc comments to every route handler:
   /**
    * @route {METHOD} {path}
    * @desc {description}
    * @access {public|private}
    */
9. Write at least one integration test per endpoint in tests/integration/
10. Commit and push

Respond with a summary of all endpoints implemented.
```

### Deliverable
- REST routes, controllers, integration tests committed and pushed

---

## Step 3: Input Validation & Auth Middleware

### Prompt

```
You are adding validation and authentication middleware to the backend API. The routes are already scaffolded.

## Auth Type
{auth_type}

## Data Models
{insert validated data models here}

## Instructions
1. Create src/middleware/auth.js:
   - Verify JWT signature and expiry
   - Attach decoded user to req.user
   - Return 401 if token is missing, invalid, or expired
2. Create src/middleware/validate.js:
   - Use Joi or Zod to create validation schemas per data model
   - Export a validate(schema) middleware factory
   - Return 400 with { "error": { "code": "VALIDATION_ERROR", "details": [...] } }
3. Apply auth middleware to all private routes (protect all routes except /auth/*, /health, /api/docs)
4. Apply validation middleware to all POST/PUT/PATCH routes using the schemas from step 2
5. Create src/utils/errors.js with custom error classes:
   - NotFoundError (404)
   - UnauthorizedError (401)
   - ValidationError (400)
   - ForbiddenError (403)
   - ApiError (base class)
6. Update the global error handler in src/app.js to:
   - Handle ApiError subclasses with their status codes
   - Log errors with appropriate detail (no sensitive data)
   - Return 500 for unknown errors with generic message
7. Add rate limiting middleware (express-rate-limit) on auth routes:
   - 5 attempts per 15 minutes per IP
   - Return 429 on limit exceeded
8. Write unit tests for auth and validation middleware in tests/unit/
9. Commit and push

Respond with a summary of middleware added.
```

### Deliverable
- Auth + validation middleware, custom error classes, rate limiting committed and pushed

---

## Step 4: Business Logic

### Prompt

```
You are implementing the business logic service layer for the backend API. The routes and controllers are already scaffolded.

## Feature Specs
{insert validated feature specs here}

## Data Models
{insert validated data models here}

## Database
{db_connection}

## Instructions
1. For each feature, create a service file under src/services/ (e.g., userService.js, projectService.js)
2. Service responsibilities:
   - All database queries via the ORM (Prisma/Sequelize)
   - Business rule enforcement per feature specs
   - Returning structured data to controllers
   - Logging significant actions (no sensitive data in logs)
3. Database connection:
   - If DATABASE_URL is set: use Prisma or Sequelize with PostgreSQL
   - If db_connection is null: implement in-memory storage with clear comments marking it as temporary
4. For each service:
   - Implement all CRUD operations as defined in feature specs
   - Add proper error handling (wrap in try/catch, throw domain-specific errors)
   - Include pagination for list operations (page, limit params)
   - Include soft-delete where appropriate
5. Ensure service methods are transactional where they touch multiple tables
6. Update controllers to call service methods (controllers should be thin — only handle HTTP)
7. Write unit tests for service layer in tests/unit/
   - Mock the ORM/database layer
   - Test business logic in isolation
   - Cover happy path and error paths
8. Update Swagger docs if any API surface changed
9. Commit and push

Respond with a summary of services implemented.
```

### Deliverable
- Service layer, tests, updated docs committed and pushed

---

## Completion

After all four steps, the agent calls the Control Plane webhook to report completion:

```
POST /agent/task/{task_id}/complete
{
  "status": "success",
  "artifacts": {
    "backend_path": "backend/",
    "endpoints": [ ... list of implemented endpoints ... ],
    "tests": { "unit": N, "integration": M }
  }
}
```

If any step fails, the agent calls:
```
POST /agent/task/{task_id}/fail
{ "error": "...", "step": "step-2" }
```

---

## Verification Checklist

Before reporting completion, verify:
- [ ] `npm install` succeeds in backend/
- [ ] `npm test` passes all tests
- [ ] `npm run dev` starts the server without errors
- [ ] Swagger UI accessible at /api/docs
- [ ] Health check returns 200 OK
- [ ] All endpoints respond with correct status codes
- [ ] Auth middleware blocks unauthenticated requests
- [ ] Validation middleware rejects invalid input
- [ ] No secrets or credentials in committed code (scan with: grep -r "sk-\|token\|password\|secret" backend/src/)
- [ ] All changes pushed to {repo_url}

---

## Notes

- Steps 1–3 are designed to run sequentially; Step 4 can run in parallel with Step 3 if feature specs are independent
- The in-memory fallback in Step 4 is only for projects without a db_connection; real deployments use NeonDB via DATABASE_URL
- Minimax M2.7 or Claude Opus can be used as the model for this chain; Sonnet is sufficient for scaffolding steps
