# Step 1: Scaffold Next.js Frontend Project

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
   │   ├── types/              # TypeScript interfaces
   │   └── styles/
   │       └── globals.css     # Global styles + CSS variables
   ├── public/
   ├── tests/
   │   ├── unit/
   │   └── e2e/
   ├── next.config.js
   ├── tailwind.config.ts
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
