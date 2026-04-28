# Unit Test Generator — Step 1: Analyze Module
## AIWA-28 | Unit Test Generation Prompt Chain

**Step:** 1 of 3
**Purpose:** Inspect the generated module, identify all exports and dependencies

---

## Context Passed by Control Plane

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "module_type": "frontend" | "backend",
  "module_path": "frontend/src/" | "backend/src/",
  "framework": "jest" | "vitest",
  "coverage_target": 80,
  "generation_artifacts": {
    "frontend_path": "frontend/",
    "components": [ ... list of component paths ... ],
    "hooks": [ ... list of hook paths ... ],
    "services": [ ... list of service paths ... ],
    "utils": [ ... list of utility paths ... ]
  },
  "mocked_dependencies": {
    "api_client": "src/lib/api.ts",
    "state_store": "src/lib/store.ts",
    "external_services": [ ... ]
  }
}
```

---

## Prompt

You are analyzing a generated module to prepare for comprehensive test generation.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- Module type: {module_type}
- Module path: {module_path}
- Test framework: {framework}

## Generation Artifacts
{insert generation artifacts from frontend/backend generation here}

## Mocked Dependencies
{insert mocked dependencies here}

## Instructions

1. Clone the repo at {repo_url} and checkout the branch with generated code

2. Scan {module_path} recursively to find all exported modules:
   - **Frontend**: components, hooks, lib utilities, API clients
   - **Backend**: routes, controllers, services, models, middleware, utils

3. For each exported module, identify:
   - All exported functions and classes
   - Function signatures (params, return types)
   - Internal dependencies (other local modules)
   - External dependencies (npm packages, HTTP calls, DB calls)
   - Side effects (logging, state mutation, async operations)

4. Build a dependency graph mapping:
   - Which modules depend on which
   - Which modules call external APIs or databases
   - Which modules have async logic requiring proper mocking

5. Identify test categories needed:
   - **Pure utility functions** → simple unit tests
   - **Component render tests** → React Testing Library
   - **Hook tests** → @testing-library/react-hooks
   - **API integration** → mocked HTTP (msw or jest.mock)
   - **Business logic** → mocked service dependencies
   - **Middleware** → unit tests with mocked req/res/next

6. Create a test plan file at `tests/.test-plan.json`:
   ```json
   {
     "modules": [ ... ],
     "coverage_target": {coverage_target},
     "framework": "{framework}",
     "estimated_tests": N
   }
   ```

7. Report the module map with dependency graph to the agent.

## Output

Respond with a summary of: number of modules, number of exports, dependency categories, and test categories identified.

### Deliverable
`tests/.test-plan.json` with module map and test plan committed and pushed