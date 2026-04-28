# Step 1: Scaffold Backend Project

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
   ```
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
   ```
3. Initialize package.json with these dependencies:
   - express, cors, helmet, compression
   - jsonwebtoken, bcryptjs
   - joi or zod (validation)
   - prisma or sequelize (ORM)
   - swagger-ui-express, swagger-jsdoc (API docs)
   - jest, supertest (testing)
   - dotenv
4. Create a base Express app in `src/app.js` with:
   - CORS, Helmet, compression middleware
   - JSON body parser
   - Swagger UI at `/api/docs`
   - 404 handler and global error handler
   - Health check endpoint at `GET /health`
5. Create `.env.example` with all required env vars:
   - PORT, NODE_ENV
   - DATABASE_URL
   - JWT_SECRET, JWT_EXPIRES_IN
   - (deployment-specific vars)
6. Create `vercel.json` for serverless Express deployment
7. Create a README.md section in the repo's README covering:
   - Setup instructions
   - Environment variables
   - How to run locally
   - API documentation link
8. Commit and push

Respond with a summary of what was created.
