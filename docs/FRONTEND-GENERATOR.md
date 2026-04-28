# Frontend Generator — Claude Code Prompt Chain
## AIWA-17 | Production-Ready React/Next.js Frontend Generator

**Status:** Draft v1.0
**Date:** 2026-04-28
**Scope:** Given a validated app idea and feature list → production-ready React/Next.js frontend

---

## Overview

This prompt chain is invoked by a Claude Code agent worker once a project has a validated app idea and feature list. The chain runs in four sequential steps:

1. **Scaffold** — Bootstrap Next.js project with design system
2. **Components** — Implement UI components per the design system
3. **API Integration** — Wire up API integration points
4. **Polish** — Responsive design, accessibility, and deployability

Output is a deployable Next.js application following the established design system.

---

## Invoker Context

The Control Plane passes this context to the agent worker at task dispatch:

```json
{
  "task_id": "<uuid>",
  "project_id": "<uuid>",
  "repo_url": "https://github.com/<org>/<repo>",
  "app_idea": { ... validated app idea ... },
  "features": [ ... validated feature list ... ],
  "design_system": { ... design tokens, colors, typography ... },
  "api_base_url": "<control-plane-api-url>",
  "deployment_target": "vercel"
}
```

---

## Step 1: Scaffold

### Prompt

```
You are building the frontend for a new web application. Your task is to scaffold a production-ready Next.js project.

## Project Context
- Project ID: {project_id}
- Repo: {repo_url}
- App Idea: {app_idea_summary}
- Design System: {design_system}

## Feature Summary
{insert validated feature list here}

## Instructions
1. Clone the repo at {repo_url}
2. Create the following directory structure under `frontend/`:
   ```
   frontend/
   ├── src/
   │   ├── app/                 # Next.js App Router pages
   │   │   ├── layout.tsx
   │   │   ├── page.tsx
   │   │   └── (route groups)/
   │   ├── components/
   │   │   ├── ui/             # Base UI primitives (Button, Input, Card, etc.)
   │   │   ├── features/       # Feature-specific components
   │   │   └── layout/         # Header, Footer, Sidebar
   │   ├── lib/
   │   │   ├── api.ts          # API client (axios/fetch wrapper)
   │   │   ├── utils.ts        # Utility functions
   │   │   └── constants.ts
   │   ├── hooks/              # Custom React hooks
   │   ├── types/             # TypeScript interfaces
   │   └── styles/
   │       └── globals.css     # Global styles + CSS variables
   ├── public/
   ├── tests/
   │   ├── unit/
   │   └── e2e/
   ├── next.config.js
   ├── tailwind.config.ts      # or other styling config
   ├── tsconfig.json
   ├── package.json
   └── vercel.json
   ```
3. Initialize package.json with these dependencies:
   - next, react, react-dom (App Router)
   - typescript, @types/react, @types/react-dom
   - tailwindcss, postcss, autoprefixer
   - axios or ky (HTTP client)
   - zustand or jotai (state management)
   - react-hook-form, zod (forms + validation)
   - @tanstack/react-query (server state)
   - lucide-react (icons)
   - clsx, tailwind-merge (classname utilities)
   - jest, @testing-library/react, @playwright/test (testing)
4. Set up the design system from {design_system}:
   - CSS variables for colors, spacing, typography
   - Base component styles
   - Utility classes
5. Create base UI primitives in `src/components/ui/`:
   - Button, Input, Select, Textarea
   - Card, Modal, Dropdown
   - Badge, Spinner, Alert
   - Table (if needed)
6. Create the root layout with:
   - Font loading (next/font)
   - Global CSS import
   - Metadata (title, description, OG tags)
   - Root providers (QueryClient, Auth context, etc.)
7. Create the home page (`src/app/page.tsx`) as a landing shell with:
   - Header with navigation placeholder
   - Main content area placeholder
   - Footer placeholder
8. Configure `next.config.js`:
   - Image domains if external assets needed
   - Rewrites for API proxying
9. Create `vercel.json` for Vercel deployment
10. Commit and push

Respond with a summary of what was created.
```

### Deliverable
- `frontend/` directory with Next.js project skeleton committed and pushed

---

## Step 2: UI Components

### Prompt

```
You are implementing UI components for the frontend. The scaffold is ready. Use the established design system and feature list.

## Design System
{insert design system tokens here}

## Feature Specs
{insert validated feature list here}

## Instructions
1. For each feature in the feature list, create the necessary components under `src/components/features/`
2. Follow the design system tokens (colors, spacing, typography, border-radius, shadows)
3. Component guidelines:
   - Use TypeScript interfaces for all props
   - Export both the component and its props interface
   - Use `clsx`/`tailwind-merge` for conditional class names
   - All interactive elements must have proper focus states
   - Loading states for async operations (skeleton or spinner)
   - Error states with clear messages
   - Empty states for list views
4. Page structure:
   - Create a page file under `src/app/` for each major feature
   - Use Next.js App Router route groups for organization
   - Each page should import and compose feature components
5. Layout components:
   - Header: navigation links, auth state indicator, mobile menu
   - Footer: links, copyright, version info
   - Sidebar (if needed): navigation for dashboard-style apps
6. Responsive design:
   - Mobile-first approach with Tailwind breakpoints
   - Hamburger menu pattern for mobile navigation
   - Responsive grid layouts
7. Add `@tanstack/react-query` hooks for data fetching per feature:
   - useProjects, useTasks, etc. (match API endpoints)
   - Include proper query key factory
   - Optimistic updates for mutations where appropriate
8. Write unit tests in `tests/unit/` for each feature component:
   - Jest + React Testing Library
   - Test rendering with mock props
   - Test interactive states (hover, click)
9. Commit and push

Respond with a summary of components created per feature.
```

### Deliverable
- Feature components, pages, React Query hooks, tests committed and pushed

---

## Step 3: API Integration

### Prompt

```
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
```

### Deliverable
- API client, typed interfaces, React Query hooks committed and pushed

---

## Step 4: Polish — Responsive, Accessibility, Deployability

### Prompt

```
You are doing final polish on the frontend. Components are built and API is wired. Ensure responsiveness, accessibility, and deployability.

## Instructions
1. Accessibility audit:
   - All images have alt text
   - All form inputs have associated labels
   - Color contrast meets WCAG AA (4.5:1 for text)
   - Focus indicators visible on all interactive elements
   - ARIA labels on icon-only buttons
   - Skip-to-content link for keyboard users
   - Proper heading hierarchy (h1 → h6)
2. Responsive design verification:
   - Test at 375px (mobile), 768px (tablet), 1280px (desktop)
   - No horizontal overflow on any breakpoint
   - Touch targets ≥ 44px on mobile
3. Performance:
   - Images use next/image with proper sizing
   - Dynamic imports for heavy components (modals, charts)
   - Route-based code splitting (automatic with Next.js App Router)
   - Font subsetting via next/font
4. SEO:
   - Metadata in `generateMetadata()` for each page
   - Open Graph tags
   - Sitemap generation (next-sitemap)
   - robots.txt
5. Error boundaries:
   - React error boundary wrapping key routes
   - Graceful degradation on component errors
6. Environment setup:
   - `.env.example` with all required NEXT_PUBLIC_ vars
   - `NEXT_PUBLIC_API_URL` for the Control Plane API
7. Vercel deployment:
   - `vercel.json` with correct build command (`next build`)
   - Environment variables configured in Vercel dashboard
   - Deployment trigger via GitHub integration
8. Final verification checklist:
   - `npm run build` succeeds with no errors
   - `npm run lint` passes
   - `npm test` passes (or skip if tests are separate)
   - Dev server starts without errors
   - No hardcoded URLs — all from env vars
9. Commit and push

## Completion

After all four steps, call the Control Plane webhook to report completion:

```
POST /agent/task/{task_id}/complete
{
  "status": "success",
  "artifacts": {
    "frontend_path": "frontend/",
    "pages": [ ... list of pages ... ],
    "components": { "ui": N, "features": M },
    "tests": { "unit": X, "e2e": Y }
  }
}
```

If any step fails, call:
```
POST /agent/task/{task_id}/fail
{ "error": "...", "step": "step-4" }
```

Respond with a summary of the complete frontend.
```

### Deliverable
- Accessible, responsive, deployable Next.js frontend committed and pushed

---

## Verification Checklist

Before reporting completion, verify:
- [ ] `npm install` succeeds in frontend/
- [ ] `npm run build` succeeds
- [ ] `npm run lint` passes
- [ ] `npm test` passes
- [ ] `npm run dev` starts without errors
- [ ] All pages render without console errors
- [ ] Auth flow: login → protected route → logout works end-to-end
- [ ] Mobile responsive at 375px, 768px, 1280px
- [ ] No secrets or credentials in committed code
- [ ] All changes pushed to {repo_url}
