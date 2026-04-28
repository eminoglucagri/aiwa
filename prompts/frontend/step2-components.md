# Step 2: UI Components

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
