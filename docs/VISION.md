# AI Web Development Automation Platform — Vision & Strategy

## Vision

Build the world's most autonomous web development engine — idea in, production-grade app out, zero manual intervention.

## Mission

Leverage Claude Code and Minimax M2.7 to automate the full web development lifecycle: idea analysis, market research, full-stack build, NeonDB integration, testing, and Vercel deployment. Users describe what they want; the platform delivers a live, deployed application.

## Success Metrics

| KPI | Target | Horizon |
|-----|--------|---------|
| Deployed apps | 50 | 6 months |
| Avg. generation time | < 30 min | 3 months |
| Test coverage | ≥ 90% | 3 months |
| Paying customers | 10 | 6 months |
| Net Promoter Score | ≥ 40 | 6 months |

## Strategic Milestones

### Milestone 1: MVP (Month 2)
- End-to-end pipeline: prompt → deployed app on Vercel
- NeonDB schema generation and connection
- Claude Code agent orchestration for multi-step generation
- Basic UI shell with responsive layout

### Milestone 2: Beta Customers (Months 3–4)
- 5–10 design-partner customers iterating on real use cases
- Automated testing pipeline (Vitest + Playwright)
- CI/CD pipeline with automated quality gates
- User feedback loop feeding product iteration

### Milestone 3: Production Reliability (Months 4–5)
- ≥ 90% test coverage across all generated apps
- Error monitoring, alerting, and graceful degradation
- Rate limiting, retry logic, and cost controls for Minimax API
- Dashboard for monitoring generation jobs and outcomes

### Milestone 4: Revenue & Growth (Month 6+)
- 10 paying customers (paid tier)
- Referral and viral loop mechanics
- Expand to additional deployment targets (Cloudflare, Railway)
- Open-source core engine for community adoption

## Non-Goals (Say No To)

- IDE plugins or editor extensions
- Mobile-first or native mobile applications
- Managed hosting infrastructure
- Marketing copy or content generation workflows

## Strategic Rationale

The web app generation space is fragmented: most tools produce prototypes, not production code. The differentiator is full-lifecycle automation — from idea to deployed, tested, database-backed application — with no human in the loop. This requires tight integration of four key systems: Claude Code (orchestration), Minimax M2.7 (generation speed/cost), NeonDB (serverless Postgres), and Vercel (deployment). Each milestone gates the next; reliability must precede growth.
