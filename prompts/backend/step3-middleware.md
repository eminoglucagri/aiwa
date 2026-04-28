# Step 3: Input Validation & Auth Middleware

You are adding validation and authentication middleware to the backend API. The routes are already scaffolded.

## Auth Type

{auth_type}

## Data Models

{insert validated data models here}

## Instructions

1. Create `src/middleware/auth.js`:
   - Verify JWT signature and expiry
   - Attach decoded user to `req.user`
   - Return 401 if token is missing, invalid, or expired
2. Create `src/middleware/validate.js`:
   - Use Joi or Zod to create validation schemas per data model
   - Export a `validate(schema)` middleware factory
   - Return 400 with `{ "error": { "code": "VALIDATION_ERROR", "details": [...] } }`
3. Apply auth middleware to all private routes (protect all routes except `/auth/*`, `/health`, `/api/docs`)
4. Apply validation middleware to all POST/PUT/PATCH routes using the schemas from step 2
5. Create `src/utils/errors.js` with custom error classes:
   - NotFoundError (404)
   - UnauthorizedError (401)
   - ValidationError (400)
   - ForbiddenError (403)
   - ApiError (base class)
6. Update the global error handler in `src/app.js` to:
   - Handle ApiError subclasses with their status codes
   - Log errors with appropriate detail (no sensitive data)
   - Return 500 for unknown errors with generic message
7. Add rate limiting middleware (`express-rate-limit`) on auth routes:
   - 5 attempts per 15 minutes per IP
   - Return 429 on limit exceeded
8. Write unit tests for auth and validation middleware in `tests/unit/`
9. Commit and push

Respond with a summary of middleware added.
