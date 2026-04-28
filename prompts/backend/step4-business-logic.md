# Step 4: Business Logic Service Layer

You are implementing the business logic service layer for the backend API. The routes and controllers are already scaffolded.

## Feature Specs

{insert validated feature specs here}

## Data Models

{insert validated data models here}

## Database

{db_connection}

## Instructions

1. For each feature, create a service file under `src/services/` (e.g., `userService.js`, `projectService.js`)
2. Service responsibilities:
   - All database queries via the ORM (Prisma/Sequelize)
   - Business rule enforcement per feature specs
   - Returning structured data to controllers
   - Logging significant actions (no sensitive data in logs)
3. Database connection:
   - If `DATABASE_URL` is set: use Prisma or Sequelize with PostgreSQL
   - If db_connection is null: implement in-memory storage with clear comments marking it as temporary
4. For each service:
   - Implement all CRUD operations as defined in feature specs
   - Add proper error handling (wrap in try/catch, throw domain-specific errors)
   - Include pagination for list operations (page, limit params)
   - Include soft-delete where appropriate
5. Ensure service methods are transactional where they touch multiple tables
6. Update controllers to call service methods (controllers should be thin — only handle HTTP)
7. Write unit tests for service layer in `tests/unit/`:
   - Mock the ORM/database layer
   - Test business logic in isolation
   - Cover happy path and error paths
8. Update Swagger docs if any API surface changed
9. Commit and push

## Completion

After all four steps, call the Control Plane webhook to report completion:

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

If any step fails, call:
```
POST /agent/task/{task_id}/fail
{ "error": "...", "step": "step-4" }
```

Respond with a summary of services implemented.
