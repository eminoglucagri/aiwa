"""Frontend scaffold generator engine.

Orchestrates the Claude Code prompt chain for generating production-ready
React/Next.js frontends from validated app ideas and feature lists.

Usage:
    engine = FrontendScaffoldEngine(
        repo_url="https://github.com/org/repo",
        api_base_url="https://api.aiwa.dev",
    )
    result = engine.run(
        project_id="<uuid>",
        app_context=app_context_dict,
    )
"""
from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Feature:
    name: str
    description: str
    priority: str = "should"


@dataclass
class Page:
    name: str
    route: str
    components: list[str] = field(default_factory=list)
    auth_required: bool = False


@dataclass
class Endpoint:
    method: str
    path: str
    purpose: str
    request_body: str = "object"
    response_body: str = "object"


@dataclass
class DesignConstraints:
    primary_color: str
    secondary_color: str
    font_family: str
    responsive_breakpoints: list[str]


@dataclass
class AppContext:
    name: str
    tagline: str
    domain: str
    features: list[Feature]
    pages: list[Page]
    api_endpoints: list[Endpoint]
    design_constraints: DesignConstraints
    deployment_target: str = "vercel"
    database: str = "neondb"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "tagline": self.tagline,
            "domain": self.domain,
            "features": [{"name": f.name, "description": f.description, "priority": f.priority} for f in self.features],
            "pages": [{"name": p.name, "route": p.route, "components": p.components, "auth_required": p.auth_required} for p in self.pages],
            "api_endpoints": [{"method": e.method, "path": e.path, "purpose": e.purpose} for e in self.api_endpoints],
            "design_constraints": {
                "primary_color": self.design_constraints.primary_color,
                "secondary_color": self.design_constraints.secondary_color,
                "font_family": self.design_constraints.font_family,
                "responsive_breakpoints": self.design_constraints.responsive_breakpoints,
            },
            "deployment_target": self.deployment_target,
            "database": self.database,
        }


@dataclass
class ScaffoldResult:
    success: bool
    files_written: list[str]
    pages_created: list[str]
    components_created: int
    errors: list[str]
    step: str = ""


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

STAGE1_SCAFFOLD_PROMPT = """You are building a production-ready Next.js frontend called {name}.
Tagline: {tagline}
Domain: {domain}

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

Write ALL files. Do not skip any file."""


STAGE2_DESIGN_SYSTEM_PROMPT = """Now configure the design system in tailwind.config.ts and src/app/globals.css.

Design tokens:
- Primary: {primary_color}
- Secondary: {secondary_color}
- Font: {font_family}

Requirements:
- Define semantic color tokens: background, foreground, muted, accent, destructive, border, ring
- Configure responsive breakpoints: {responsive_breakpoints}
- Set up Tailwind content paths for app router
- Add @font-face for custom font family
- Set CSS custom properties for all semantic tokens
- NO arbitrary Tailwind values (no [color:xxx] inline styles)

Write: tailwind.config.ts, src/app/globals.css"""


STAGE3_LAYOUT_PROMPT = """Build the root layout and navigation shell.

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

Write: src/app/layout.tsx, src/components/layout/Header.tsx, src/components/layout/Footer.tsx, src/components/layout/Container.tsx"""


STAGE4_PAGES_PROMPT = """Now implement each page from the app context pages.

For each page:
1. Create the page file at src/app/{route}/page.tsx
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

Each page must be fully implemented — no TODOs, no placeholders."""


STAGE5_COMPONENTS_PROMPT = """Implement all feature-specific components.

For each feature:
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
- Be fully typed — no `any` types"""


STAGE6_API_INTEGRATION_PROMPT = """Build the API integration layer.

File: src/lib/api.ts

For each endpoint:
- Define typed fetch functions
- Handle auth token injection
- Handle network errors, 401 (redirect to login), 429 (retry after), 500 (friendly error)
- Define `ApiError` class with status, message, and raw error fields
- Define `getAuthToken()` from localStorage (client) or cookies (server)
- Add `getBaseUrl()` helper for environment-aware API base URL
- Export a typed `ApiClient` object with all endpoint methods

File: src/hooks/use-api.ts

Per-endpoint React Query hooks using @tanstack/react-query v5:
- Configure staleTime: 30_000, gcTime: 300_000, retry: 2
- Handle 401 globally: refetchAuth → if fails, redirect to /login

Write: src/lib/api.ts, src/hooks/use-api.ts, src/types/index.ts (all interface types)"""


STAGE7_AUTH_PROMPT = """Implement the authentication flow.

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

Write: src/lib/auth.ts, src/contexts/AuthContext.tsx, auth page components"""


STAGE8_RESPONSIVE_PROMPT = """After all components are written, run this verification step.

Check every component for responsive correctness:
1. No fixed pixel widths on content containers — use max-w-* or percentage-based
2. Grid/flex layouts use responsive modifiers (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
3. Typography scales: text-sm (mobile), md:text-base, lg:text-lg
4. Padding/margins: mobile-first (p-4 → md:p-6 → lg:p-8)
5. Images: aspect-ratio preserved, use next/image with responsive sizes
6. Tables: horizontal scroll on mobile, stack to cards on xs
7. Navigation: hamburger on mobile, full nav on md+

Add responsive classes where missing. Do not break desktop layouts."""


STAGE9_A11Y_PROMPT = """Run accessibility checks on every component.

Requirements (WCAG 2.1 AA):
1. All images have alt text (use next/image or img with alt)
2. All form inputs have associated <label> elements
3. All buttons have accessible names (aria-label if icon-only)
4. Focus indicators: visible ring on all interactive elements (outline-none ring-2 ring-offset-2)
5. Color contrast: all text passes 4.5:1 ratio
6. Keyboard navigation: tab order follows visual order, Escape closes modals
7. ARIA live regions for dynamic content (loading states, toast notifications)
8. Semantic HTML: use <main>, <nav>, <header>, <footer>, <article>, <section> appropriately
9. Skip to main content link (sr-only href="#main-content")
10. Form error messages linked with aria-describedby

Apply fixes to all components."""


STAGE10_DEPLOY_PROMPT = """Write deployment configuration files.

vercel.json:
- Set build command: "npm run build"
- Set output directory: ".next"
- Configure headers for security (CSP, HSTS, X-Frame-Options)
- Set rewrites for API proxy to /api/* → control plane

package.json:
- Name: {app_name_lower}
- Scripts: dev, build, start, lint, type-check
- Dependencies: next@14, react@18, react-dom@18, tailwindcss@3, @tanstack/react-query@5, react-hook-form@7, @hookform/resolvers, zod, next/font, shadcn/ui, sonner, @tanstack/react-virtual
- DevDependencies: @types/node, typescript, @typescript-eslint/eslint-plugin, tailwindcss, postcss, autoprefixer

next.config.ts:
- Enable strict mode
- Configure images: domains for external images
- Set poweredByHeader: false (security)
- Configure experimental features if needed (serverActions, etc.)

Write: vercel.json, package.json, next.config.ts"""


STAGE11_VALIDATION_PROMPT = """After all files are written, perform a final validation pass.

1. Run: npx tsc --noEmit to verify TypeScript correctness
2. Verify all imports resolve — no missing imports, no circular deps
3. Verify all API endpoint types match the specification
4. Confirm every page has a corresponding file
5. Confirm every feature has a corresponding component
6. Verify all shadcn/ui components are imported from @/components/ui/* (not duplicated inline)
7. Confirm no TODO or FIXME comments remain
8. Verify package.json scripts cover: dev, build, start, lint, type-check

If errors found: fix them. If types are missing: define them in src/types/index.ts."""


# ---------------------------------------------------------------------------
# Claude Code invoker
# ---------------------------------------------------------------------------

class ClaudeCodeInvoker:
    """Invokes Claude Code CLI with a prompt, writing output to a project directory."""

    def __init__(self, repo_url: str, working_dir: Optional[str] = None):
        self.repo_url = repo_url
        self.working_dir = working_dir or tempfile.mkdtemp(prefix="aiwa-frontend-")

    def run_prompt(self, prompt: str, stage_name: str, timeout_seconds: int = 300) -> tuple[bool, str]:
        """Execute a Claude Code prompt in the working directory.

        Returns (success, output).
        """
        env = {
            "CLAUDE_CODE_DISABLE_WARNING": "1",
            "CLAUDE_CODE_NO_VERSION_CHECK": "1",
        }
        try:
            result = subprocess.run(
                ["claude", "--print", prompt],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=self.working_dir,
                env=env,
            )
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            logger.warning("Stage %s timed out after %ds", stage_name, timeout_seconds)
            return False, f"Timeout after {timeout_seconds}s"
        except FileNotFoundError:
            logger.error("Claude Code CLI not found. Ensure it's installed and in PATH.")
            return False, "claude command not found"
        except Exception as e:
            logger.error("Error running Claude Code: %s", e)
            return False, str(e)


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

class FrontendScaffoldEngine:
    """Orchestrates the frontend scaffold generation pipeline.

    Usage:
        engine = FrontendScaffoldEngine(
            repo_url="https://github.com/org/repo",
            api_base_url="https://api.aiwa.dev",
        )
        result = engine.run(
            project_id="<uuid>",
            app_context=app_context_dict,
        )
    """

    STAGES = [
        ("scaffold", STAGE1_SCAFFOLD_PROMPT, 300),
        ("design_system", STAGE2_DESIGN_SYSTEM_PROMPT, 180),
        ("layout", STAGE3_LAYOUT_PROMPT, 180),
        ("pages", STAGE4_PAGES_PROMPT, 300),
        ("components", STAGE5_COMPONENTS_PROMPT, 300),
        ("api_integration", STAGE6_API_INTEGRATION_PROMPT, 240),
        ("auth", STAGE7_AUTH_PROMPT, 180),
        ("responsive", STAGE8_RESPONSIVE_PROMPT, 120),
        ("accessibility", STAGE9_A11Y_PROMPT, 120),
        ("deployment", STAGE10_DEPLOY_PROMPT, 120),
        ("validation", STAGE11_VALIDATION_PROMPT, 180),
    ]

    def __init__(self, repo_url: str, api_base_url: str, working_dir: Optional[str] = None):
        self.repo_url = repo_url
        self.api_base_url = api_base_url
        self.invoker = ClaudeCodeInvoker(repo_url, working_dir)

    def run(
        self,
        project_id: str,
        app_context: dict | AppContext,
        project_dir: Optional[str] = None,
    ) -> ScaffoldResult:
        """Run the full frontend scaffold generation pipeline.

        Args:
            project_id: UUID of the project in the control plane.
            app_context: AppContext dict or AppContext instance with name, tagline,
                         domain, features, pages, api_endpoints, design_constraints.
            project_dir: Override working directory for the generated frontend.
        """
        if isinstance(app_context, dict):
            app_context = self._dict_to_context(app_context)

        errors: list[str] = []
        files_written: list[str] = []
        pages_created: list[str] = []
        components_created = 0

        working_dir = project_dir or self.invoker.working_dir

        for stage_name, prompt_template, timeout in self.STAGES:
            prompt = self._fill_template(prompt_template, app_context)
            logger.info("Running stage: %s", stage_name)

            success, output = self.invoker.run_prompt(prompt, stage_name, timeout)
            if not success:
                errors.append(f"Stage '{stage_name}' failed: {output}")
                return ScaffoldResult(
                    success=False,
                    files_written=files_written,
                    pages_created=pages_created,
                    components_created=components_created,
                    errors=errors,
                    step=stage_name,
                )

            # Count generated files
            if stage_name == "scaffold":
                files_written.extend(self._discover_frontend_files(working_dir))
            if stage_name == "pages":
                pages_created.extend(self._discover_pages(working_dir))
            if stage_name == "components":
                components_created = self._count_feature_components(working_dir)

        # Final inventory
        files_written = self._discover_frontend_files(working_dir)

        return ScaffoldResult(
            success=True,
            files_written=files_written,
            pages_created=pages_created,
            components_created=components_created,
            errors=[],
        )

    def run_stage(self, stage: str, app_context: dict | AppContext) -> tuple[bool, str]:
        """Run a single stage by name. Returns (success, output)."""
        if isinstance(app_context, dict):
            app_context = self._dict_to_context(app_context)

        stage_map = {name: (tmpl, timeout) for name, tmpl, timeout in self.STAGES}
        if stage not in stage_map:
            return False, f"Unknown stage: {stage}. Available: {list(stage_map.keys())}"

        prompt_template, timeout = stage_map[stage]
        prompt = self._fill_template(prompt_template, app_context)
        return self.invoker.run_prompt(prompt, stage, timeout)

    def _dict_to_context(self, d: dict) -> AppContext:
        dc_data = d.get("design_constraints", {})
        design_constraints = DesignConstraints(
            primary_color=dc_data.get("primary_color", "#0A0A0A"),
            secondary_color=dc_data.get("secondary_color", "#3B82F6"),
            font_family=dc_data.get("font_family", "Inter"),
            responsive_breakpoints=dc_data.get("responsive_breakpoints", ["sm", "md", "lg", "xl"]),
        )

        features = [Feature(name=f["name"], description=f.get("description", ""), priority=f.get("priority", "should"))
                    for f in d.get("features", [])]
        pages = [Page(name=p["name"], route=p["route"], components=p.get("components", []), auth_required=p.get("auth_required", False))
                 for p in d.get("pages", [])]
        endpoints = [Endpoint(method=e["method"], path=e["path"], purpose=e.get("purpose", ""))
                     for e in d.get("api_endpoints", [])]

        return AppContext(
            name=d.get("name", "App"),
            tagline=d.get("tagline", ""),
            domain=d.get("domain", "saas"),
            features=features,
            pages=pages,
            api_endpoints=endpoints,
            design_constraints=design_constraints,
            deployment_target=d.get("deployment_target", "vercel"),
            database=d.get("database", "neondb"),
        )

    def _fill_template(self, template: str, ctx: AppContext) -> str:
        dc = ctx.design_constraints
        context = ctx.to_dict()

        replacements = {
            "{name}": ctx.name,
            "{tagline}": ctx.tagline,
            "{domain}": ctx.domain,
            "{primary_color}": dc.primary_color,
            "{secondary_color}": dc.secondary_color,
            "{font_family}": dc.font_family,
            "{responsive_breakpoints}": ", ".join(dc.responsive_breakpoints),
            "{app_name_lower}": ctx.name.lower().replace(" ", "-"),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(key, str(value))

        # Inject features/pages/endpoints as structured data
        if "{features}" in result:
            feature_lines = "\n".join(
                f"- {f.name}: {f.description} (priority: {f.priority})"
                for f in ctx.features
            )
            result = result.replace("{features}", feature_lines)

        if "{pages}" in result:
            page_lines = "\n".join(
                f"- {p.name} at {p.route} (auth_required={p.auth_required})"
                for p in ctx.pages
            )
            result = result.replace("{pages}", page_lines)

        if "{api_endpoints}" in result:
            endpoint_lines = "\n".join(
                f"- {e.method} {e.path}: {e.purpose}"
                for e in ctx.api_endpoints
            )
            result = result.replace("{api_endpoints}", endpoint_lines)

        return result

    def _discover_frontend_files(self, working_dir: str) -> list[str]:
        frontend_dir = Path(working_dir) / "frontend"
        if not frontend_dir.exists():
            return []
        files = []
        for f in frontend_dir.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                rel = f.relative_to(frontend_dir)
                files.append(str(rel))
        return sorted(files)

    def _discover_pages(self, working_dir: str) -> list[str]:
        frontend_dir = Path(working_dir) / "frontend" / "src" / "app"
        if not frontend_dir.exists():
            return []
        pages = []
        for f in frontend_dir.rglob("page.tsx"):
            rel = f.relative_to(frontend_dir)
            pages.append(str(rel).replace("/", "/").replace("\\", "/"))
        return sorted(pages)

    def _count_feature_components(self, working_dir: str) -> int:
        features_dir = Path(working_dir) / "frontend" / "src" / "components" / "features"
        if not features_dir.exists():
            return 0
        return len([f for f in features_dir.iterdir() if f.is_file() and f.suffix in (".tsx", ".ts")])


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def run_frontend_scaffold(
    project_id: str,
    app_context: dict,
    repo_url: str,
    api_base_url: str,
    project_dir: Optional[str] = None,
) -> ScaffoldResult:
    """Run the frontend scaffold generator.

    Shorthand for:
        engine = FrontendScaffoldEngine(repo_url, api_base_url)
        return engine.run(project_id, app_context, project_dir)
    """
    engine = FrontendScaffoldEngine(repo_url=repo_url, api_base_url=api_base_url)
    return engine.run(project_id=project_id, app_context=app_context, project_dir=project_dir)