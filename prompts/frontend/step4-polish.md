# Step 4: Responsive, Accessibility, and Deployability

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
   - Touch targets >= 44px on mobile
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
