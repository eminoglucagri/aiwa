# Step 2: REST Endpoints

You are implementing REST endpoints for the backend API. Using the scaffolded project structure, implement all endpoints defined in the feature specs.

## Feature Specs

{insert validated feature specs here}

## Data Models

{insert validated data models here}

## Instructions

1. For each feature, create a route file under `src/routes/` named after the resource (e.g., `users.js`, `projects.js`)
2. Each route file should use an Express Router
3. For each endpoint, create a corresponding controller in `src/controllers/`
4. Controllers must:
   - Extract and validate request parameters (params, query, body)
   - Call the appropriate service method
   - Return JSON responses with proper HTTP status codes
   - Wrap all logic in try/catch and call `next(err)` on failure
5. HTTP status code conventions:
   - GET: 200 OK, 404 Not Found
   - POST: 201 Created, 400 Bad Request, 401 Unauthorized
   - PUT/PATCH: 200 OK, 400 Bad Request, 404 Not Found
   - DELETE: 204 No Content, 404 Not Found
6. Error responses must follow this format:
   ```json
   { "error": { "code": "RESOURCE_NOT_FOUND", "message": "Human readable message" } }
   ```
7. Register all routers in `src/app.js`
8. Add Swagger JSdoc comments to every route handler:
   ```js
   /**
    * @route {METHOD} {path}
    * @desc {description}
    * @access {public|private}
    */
   ```
9. Write at least one integration test per endpoint in `tests/integration/`
10. Commit and push

Respond with a summary of all endpoints implemented.
