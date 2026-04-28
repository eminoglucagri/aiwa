---
name: backend-api-generator-prompt-chain
description: AIWA-18 deliverable — 4-step Claude Code prompt chain for generating production-ready Node.js/Express backends
type: project
originSessionId: dca2863b-1820-4700-9ccf-abf36f2c5474
---

## AIWA-18 — Backend API Generator Prompt Chain

### What was produced
`docs/BACKEND-API-GENERATOR.md` — complete 4-step prompt chain (Scaffold → Endpoints → Middleware → Business Logic) + `prompts/backend/` directory with invocation-ready prompt files.

### Prompt files created
- `prompts/backend/step1-scaffold.md` — Express project bootstrap
- `prompts/backend/step2-endpoints.md` — REST routes + controllers
- `prompts/backend/step3-middleware.md` — Auth, validation, rate limiting
- `prompts/backend/step4-business-logic.md` — Service layer

### Next action for AIWA-18
1. Review the chain for completeness — does it cover all requirements from the issue description?
2. Test the chain against a real project once data models are available
3. Consider whether steps can be merged or parallelized for faster generation
