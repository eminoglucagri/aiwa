# Frontend Scaffold Generator — AIWA-17

**Document:** AIWA-17 Frontend Scaffold Generator v1.0
**Date:** 2026-04-28
**Status:** Complete
**Author:** Full-Stack Engineer (agent dca2863b)

## Purpose

A Claude Code prompt chain that transforms a validated app idea and feature list into a production-ready React/Next.js frontend. It takes output from prior pipeline stages (market research, technical spec, design decisions) and produces deployable, accessible, responsive code.

## Input Contract

The chain expects a structured `APP_CONTEXT` block containing:

```
APP_CONTEXT:
  name: string              # e.g., "QuickCart"
  tagline: string            # e.g., "Sell products fast"
  domain: string             # e.g., "e-commerce", "saas-dashboard", "booking"
  features: Feature[]       # each has { name, description, priority }
  pages: Page[]              # each has { name, route, components, auth_required }
  api_endpoints: Endpoint[]  # each has { method, path, purpose, request_body, response_body }
  design_constraints:
    primary_color: string
    secondary_color: string
    font_family: string
    responsive_breakpoints: string[]
  deployment_target: "vercel"
  database: "neondb"         # for hydration/fetch patterns
```

## Output Contract

The chain produces a complete Next.js 14 + TypeScript + Tailwind CSS project with:

1. **Project structure** (file tree matches ARCHITECTURE.md §3.2 code storage layout)
2. **All pages and routes** per the `pages` spec
3. **All UI components** per the design system
4. **API integration layer** (typed fetch wrappers per `api_endpoints`)
5. **Responsive design** (mobile-first, all breakpoints)
6. **Accessibility** (WCAG 2.1 AA)
7. **Deployment-ready** (`vercel.json`, `package.json`, `next.config.ts`)

---

## Prompt Chain

### Stage 1 — Project Bootstrap

```
You are building a production-ready Next.js frontend called {APP_CONTEXT.name}.
Tagline: {APP_CONTEXT.tagline}
Domain: {APP_CONTEXT.domain}

Constraints:
- Next.js 14 App Router (TypeScript strict mode)
- Tailwind CSS v3 with custom design tokens
- No CSS-in-JS, no Tailwind utilities outside @apply in component files
- Use shadcn/ui components as primitives
- Response: TypeScript only, no comments in output code

Initialize the project with this exact structure:

/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # root layout, fonts, metadata
│   │   ├── page.tsx            # landing/home page
│   │   └── (auth)/             # route group for auth pages
│   │       ├── login/page.tsx
│   │       └── register/page.tsx
│   ├── components/
│   │   ├── ui/                 # shadcn/ui primitives (Button, Input, Card, etc.)
│   │   ├── layout/            # Header, Footer, Sidebar, Container
│   │   └── features/          # domain-specific components
│   ├── lib/
│   │   ├── api.ts             # typed fetch wrappers
│   │   ├── auth.ts            # auth utilities
│   │   └── utils.ts          # cn() helper, class merging
│   ├── hooks/
│   │   └── use-api.ts         # data fetching hooks
│   └── types/
│       └── index.ts           # all TypeScript interfaces
├── public/
│   ├── favicon.ico
│   └── og-image.png
├── tailwind.config.ts
├── next.config.ts
├── vercel.json
├── package.json
└── tsconfig.json

Write ALL files. Do not skip any file.
```

### Stage 2 — Design System Setup

```
Now configure the design system in tailwind.config.ts and src/app/globals.css.

Design tokens:
- Primary: {APP_CONTEXT.design_constraints.primary_color}
- Secondary: {APP_CONTEXT.design_constraints.secondary_color}
- Font: {APP_CONTEXT.design_constraints.font_family}

Requirements:
- Define semantic color tokens: background, foreground, muted, accent, destructive, border, ring
- Configure responsive breakpoints: {APP_CONTEXT.design_constraints.responsive_breakpoints}
- Set up Tailwind content paths for app router
- Add @font-face for custom font family
- Set CSS custom properties for all semantic tokens
- NO arbitrary Tailwind values (no [color:xxx] inline styles)

Write: tailwind.config.ts, src/app/globals.css
```

### Stage 3 — Layout Shell

```
Build the root layout and navigation shell.

Root layout (src/app/layout.tsx):
- Import and apply the font family from next/font/google
- Set metadata: title, description, og:image, favicon
- Apply Tailwind base styles and CSS custom properties
- Import globals.css
- Wrap children in the app shell

Header component (src/components/layout/Header.tsx):
- Responsive: mobile hamburger menu, desktop horizontal nav
- Contains: logo (from app name), nav links, auth buttons (Login/Sign up or user avatar)
- Uses shadcn/ui Sheet for mobile menu
- Sticky with backdrop blur
- Mobile: hamburger icon → Sheet drawer
- Desktop (md:): horizontal nav links

Footer component (src/components/layout/Footer.tsx):
- Responsive grid layout: brand, links, legal
- Contains: copyright, social links, footer nav

Container component (src/components/layout/Container.tsx):
- Max-width wrapper with responsive padding
- Breakpoints: px-4 (mobile), px-6 (tablet), px-8 (desktop)

Write: src/app/layout.tsx, src/components/layout/Header.tsx, src/components/layout/Footer.tsx, src/components/layout/Container.tsx
```

### Stage 4 — Page Implementation

```
Now implement each page from APP_CONTEXT.pages.

For each page "{PAGE.name}" (route: {PAGE.route}):

1. Create the page file at src/app/{PAGE.route}/page.tsx
2. Import the layout shell (Header, Footer, Container)
3. Implement the page content using components from src/components/features/
4. For authenticated pages: check auth state, redirect to /login if unauthenticated
5. Use Suspense boundaries for data fetching
6. Add proper metadata export

Page requirements:
- Landing page (/): Hero section with tagline, CTA buttons, feature highlights
- Login (/login): Email + password form, "forgot password" link, "register" link
- Register (/register): Name, email, password, confirm password form
- Authenticated pages: use the auth session from src/lib/auth.ts

Each page must be fully implemented — no TODOs, no placeholders.
Write every page file from APP_CONTEXT.pages.
```

### Stage 5 — Feature Components

```
Implement all feature-specific components from APP_CONTEXT.features.

For each feature "{FEATURE.name}":
- Create src/components/features/{FeatureName}.tsx
- Use TypeScript interfaces derived from the feature description
- Wire to the API layer (src/lib/api.ts)
- Handle loading, error, and empty states
- Include skeleton loaders using shadcn/ui Skeleton
- Use React Server Components where data doesn't need interactivity

Component patterns:
- Data display: Table with shadcn/ui Table components, pagination
- Forms: React Hook Form + Zod validation + shadcn/ui Form components
- Lists: Virtual scrolling with @tanstack/react-virtual for >20 items
- Modals: shadcn/ui Dialog, AlertDialog
- Notifications: shadcn/ui Sonner (toast library)

Each component must:
- Export an interface for its props (documented with JSDoc)
- Handle all states: loading (skeleton), error (error card), empty (empty state), data
- Use proper ARIA labels and roles for accessibility
- Be fully typed — no `any` types

Write all feature components.
```

### Stage 6 — API Integration Layer

```
Build the API integration layer using APP_CONTEXT.api_endpoints.

File: src/lib/api.ts

For each endpoint {ENDPOINT.method} {ENDPOINT.path}:

```typescript
export async function {endpointFunctionName}(
  body: {ENDPOINT.request_body}
): Promise<{ENDPOINT.response_body}> {
  const res = await fetch('{ENDPOINT.path}', {
    method: '{ENDPOINT.method}',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new ApiError(res.status, error.message, error);
  }
  return res.json();
}
```

Additional requirements:
- Define `ApiError` class with status, message, and raw error fields
- Define `getAuthToken()` from localStorage (client) or cookies (server)
- Add `getBaseUrl()` helper for environment-aware API base URL
- Export a typed `ApiClient` object with all endpoint methods
- Handle network errors, 401 (redirect to login), 429 (retry after), 500 (friendly error)

File: src/hooks/use-api.ts

```typescript
// Per-endpoint React Query hooks:
// use{FeatureName}(params) → { data, isLoading, error, refetch }
// use{FeatureName}Mutation() → { mutate, isPending, error }

- Use @tanstack/react-query v5
- Configure staleTime: 30_000, gcTime: 300_000, retry: 2
- Handle 401 globally: refetchAuth → if fails, redirect to /login
```

Write: src/lib/api.ts, src/hooks/use-api.ts, src/types/index.ts (all interface types)
```

### Stage 7 — Authentication Flow

```
Implement the authentication flow.

Files to create/update:

src/lib/auth.ts:
- getAuthToken(): string | null
- setAuthToken(token: string): void
- clearAuthToken(): void
- getCurrentUser(): User | null (from JWT decode)
- isAuthenticated(): boolean

Login page (src/app/(auth)/login/page.tsx):
- Form: email, password fields with Zod validation
- On submit: call API, store token, redirect to dashboard or intended URL
- Error handling: show inline error messages
- Loading state: disable form, show spinner

Register page (src/app/(auth)/register/page.tsx):
- Form: name, email, password, confirmPassword fields
- Validation: password === confirmPassword, password min 8 chars
- On submit: call API, store token, redirect to onboarding or dashboard

Auth context (src/contexts/AuthContext.tsx):
- Create AuthProvider with React Context
- Expose: user, isLoading, login, logout, register
- On mount: check for existing token, validate session
- Persist token to localStorage
- Redirect logic for protected routes

Write: src/lib/auth.ts, src/contexts/AuthContext.tsx, auth page components
```

### Stage 8 — Responsive Design Verification

```
After all components are written, run this verification step.

Check every component for responsive correctness:
1. No fixed pixel widths on content containers — use max-w-* or percentage-based
2. Grid/flex layouts use responsive modifiers (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
3. Typography scales: text-sm (mobile), md:text-base, lg:text-lg
4. Padding/margins: mobile-first (p-4 → md:p-6 → lg:p-8)
5. Images: aspect-ratio preserved, use next/image with responsive sizes
6. Tables: horizontal scroll on mobile, stack to cards on xs
7. Navigation: hamburger on mobile, full nav on md+

Add responsive classes where missing. Do not break desktop layouts.
```

### Stage 9 — Accessibility Audit

```
Run accessibility checks on every component.

Requirements (WCAG 2.1 AA):
1. All images have alt text (use next/image or img with alt)
2. All form inputs have associated <label> elements
3. All buttons have accessible names (aria-label if icon-only)
4. Focus indicators: visible ring on all interactive elements (outline-none ring-2 ring-offset-2)
5. Color contrast: all text passes 4.5:1 ratio (use Tailwind's built-in contrast-safe colors)
6. Keyboard navigation: tab order follows visual order, Escape closes modals
7. ARIA live regions for dynamic content (loading states, toast notifications)
8. Semantic HTML: use <main>, <nav>, <header>, <footer>, <article>, <section> appropriately
9. Skip to main content link (sr-only href="#main-content")
10. Form error messages linked with aria-describedby

Apply fixes to all components. Verify with axe-core if available.
```

### Stage 10 — Deployment Configuration

```
Write deployment configuration files.

vercel.json:
- Set build command: "npm run build"
- Set output directory: ".next"
- Configure headers for security (CSP, HSTS, X-Frame-Options)
- Set rewrites for API proxy to /api/* → control plane

package.json:
- Name: {APP_CONTEXT.name.toLowerCase().replace(/\s+/g, '-')}-frontend
- Scripts: dev, build, start, lint, type-check
- Dependencies: next@14, react@18, react-dom@18, tailwindcss@3, @tanstack/react-query@5, react-hook-form@7, @hookform/resolvers, zod, next/font, shadcn/ui, sonner, @tanstack/react-virtual
- DevDependencies: @types/node, typescript, @typescript-eslint/eslint-plugin, tailwindcss, postcss, autoprefixer

next.config.ts:
- Enable strict mode
- Configure images: domains for external images
- Set poweredByHeader: false (security)
- Configure experimental features if needed (serverActions, etc.)

Write: vercel.json, package.json, next.config.ts
```

### Stage 11 — Type Check and Validation

```
After all files are written, perform a final validation pass.

1. Run: npx tsc --noEmit to verify TypeScript correctness
2. Verify all imports resolve — no missing imports, no circular deps
3. Verify all API endpoint types match the APP_CONTEXT specification
4. Confirm every page in APP_CONTEXT.pages has a corresponding file
5. Confirm every feature in APP_CONTEXT.features has a corresponding component
6. Verify all shadcn/ui components are imported from @/components/ui/* (not duplicated inline)
7. Confirm no TODO or FIXME comments remain
8. Verify package.json scripts cover: dev, build, start, lint, type-check

If errors found: fix them. If types are missing: define them in src/types/index.ts.
```

---

## Design System Reference

When implementing, follow these conventions (derived from ARCHITECTURE.md):

| Token | Usage | Tailwind class |
|---|---|---|
| Background | Page backgrounds | `bg-background` |
| Foreground | Primary text | `text-foreground` |
| Muted | Secondary text, borders | `text-muted-foreground`, `bg-muted` |
| Accent | Highlights, CTAs | `bg-accent`, `text-accent-foreground` |
| Destructive | Errors, danger actions | `bg-destructive`, `text-destructive-foreground` |
| Card | Card surfaces | `bg-card`, `text-card-foreground` |

Font family: Inter (default) or as specified in APP_CONTEXT.

---

## Error Handling Standards

Every API call must handle:
- **Network errors**: show toast "Network error — please try again"
- **401 Unauthorized**: clear token, redirect to /login
- **403 Forbidden**: show toast "You don't have permission for this action"
- **404 Not Found**: show "Resource not found" with back navigation
- **429 Rate Limited**: show toast with retry countdown
- **500 Server Error**: show toast "Something went wrong — our team has been notified"
- **Validation errors (422)**: inline field errors from API response

Never show raw error messages or stack traces to users.

---

## Testing Requirements

Each component must have tests (Vitest + React Testing Library):

```
ComponentName.test.tsx:
- Renders correctly with required props
- Shows loading skeleton when isLoading=true
- Shows error state when error is provided
- Shows empty state when data array is empty
- Interactive: button clicks trigger callbacks
- Accessibility: passes axe-core audit
```

Write test files for every feature component. Use `vi.mock()` for API calls.

---

## Completion Criteria

The chain is complete when:
- [ ] All files in the project structure exist and are non-empty
- [ ] `npx tsc --noEmit` passes with zero errors
- [ ] `npm run lint` passes with zero errors
- [ ] `npm run build` completes successfully
- [ ] Every page from APP_CONTEXT.pages is implemented
- [ ] Every feature from APP_CONTEXT.features has a component
- [ ] All API endpoints have typed fetch wrappers
- [ ] Auth flow (login, register, logout, protected routes) works
- [ ] All responsive breakpoints verified
- [ ] All accessibility requirements met (WCAG 2.1 AA)
- [ ] vercel.json configured for deployment
- [ ] package.json has all required scripts and dependencies