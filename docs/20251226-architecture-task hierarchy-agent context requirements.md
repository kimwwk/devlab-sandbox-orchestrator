# Task Hierarchy: Agent Context Requirements

## Context

This document defines what different agent roles need from the task system to operate effectively. Context requirements vary significantly by role.

**Key insight:** Agents don't just need task data - they need role-appropriate **context bundles** assembled for their specific job.

Related: [Tracking Integration](./20251226-architecture-task%20hierarchy-tracking%20integration.md) | [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md)

---

## Work Unit Granularity

Before role-specific needs, the right task size matters for all agents:

| Level | Agent Fit | Reasoning |
|-------|-----------|-----------|
| Epic | No | Too large, cannot complete in one session |
| Feature | Maybe | Depends on complexity, often needs breakdown |
| User Story | Yes | Goal-oriented, achievable, agent decides *how* |
| Task | Risky | Too atomic, agent becomes executor not decision-maker |

**Principle:** Agent receives goal + constraints, decides approach. If task is so small agent has no decisions to make, it's too granular.

---

## Senior Developer Agent

**Role:** Implements features, writes code, creates PRs.

**Scenario:** Agent receives task "Implement user authentication with JWT"

### What Agent Needs to Know

| Question | Why It Matters | Source |
|----------|----------------|--------|
| What's the goal? | Understand what "done" looks like | User story, acceptance criteria |
| Why does this exist? | Make design decisions aligned with purpose | Product context, business need |
| What already exists? | Don't rebuild, integrate properly | Codebase summary, existing related code |
| What patterns to follow? | Match team conventions | Project conventions, existing patterns |
| What tech constraints? | Choose compatible solutions | Tech stack docs, architecture decisions |
| What's explicitly out of scope? | Avoid over-engineering | Future-features, task boundaries |
| What depends on this? | Understand downstream impact | Dependency graph, related tasks |
| What blocks this? | Know if can proceed | Prerequisite task status |

### Example Context Bundle

```
Task: Implement JWT authentication

Goal: Users can log in and receive a token for API access

Existing code:
- User model exists at src/models/user.ts
- API routes pattern: src/routes/*.ts
- No current auth - this is greenfield

Conventions:
- Use bcrypt for hashing (not argon2)
- Tokens stored in httpOnly cookies
- Error format: { error: string, code: number }

Out of scope:
- OAuth/social login (Future-Features.md)
- Password reset flow (separate task)
- Session management UI (frontend task)

Acceptance:
- POST /auth/login returns JWT on valid credentials
- JWT expires in 24h
- Invalid credentials return 401
```

---

## QA Engineer Agent

**Role:** Tests features, validates behavior, reports issues.

**Scenario:** Agent receives task "Test the JWT authentication feature"

### Operational Context

QA agents typically:
- Work in their own **test repository** (not the main codebase)
- Test against **deployed environments** (dev/staging), not localhost
- Have access to test frameworks, fixtures, and reporting tools
- May create test cases, automation scripts, or manual test reports

### What Agent Needs to Know

| Question | Why It Matters | Source |
|----------|----------------|--------|
| What was built? | Know what to test | Completed task description, changelog |
| What should happen? | Define expected behavior | Acceptance criteria, user story |
| Where is it deployed? | Access the feature | Environment URL (dev, staging) |
| What could go wrong? | Focus on risk areas | Edge cases, security concerns, past bugs |
| What test data exists? | Set up scenarios | Test environment data, fixtures |
| What's already covered? | Avoid duplicate effort | Existing test suites, automation |
| What's out of scope? | Don't test unrelated things | Task boundaries |
| How to report findings? | Deliver results properly | Bug report format, where to log issues |

### Example Context Bundle

```
Feature: JWT Authentication (Task 2.3)
PR: #47 (merged to develop)

What was implemented:
- POST /auth/login endpoint
- JWT token generation
- Password verification with bcrypt

Test environment:
- URL: https://dev.example.com
- API base: https://dev.example.com/api/v1

Test accounts available:
- test@example.com / password123 (valid user)
- admin@example.com / admin456 (admin role)
- No user: nonexistent@example.com

Test scenarios to cover:
1. Valid login → returns token, 200
2. Wrong password → returns 401, no token leaked
3. Unknown user → returns 401 (same error as wrong password)
4. Missing fields → returns 400 with validation errors
5. Token format is valid JWT structure
6. Token contains expected claims (userId, exp)
7. Expired token rejected by protected endpoints

Security checks:
- Password not in any response body
- Token not logged to console/server logs
- Rate limiting on failed attempts (if implemented)

Not testing (out of scope):
- Token refresh (not implemented yet)
- UI login form (frontend task)
- OAuth flows (future feature)

Report findings to:
- Bugs: Create issue in project repo with label "bug"
- Test results: Update task with summary
```

---

## Bug Fixer Agent

**Role:** Diagnoses and fixes reported bugs.

**Scenario:** Agent receives bug "Login returns 500 error for emails with plus sign"

### Operational Context

Bug fixer agents typically:
- Start from a bug report, not a feature spec
- Need reproduction steps and environment details
- Must understand expected vs actual behavior
- Should minimize change scope (fix bug, don't refactor)

### What Agent Needs to Know

| Question | Why It Matters | Source |
|----------|----------------|--------|
| What's the bug? | Understand the problem | Bug report title, description |
| How to reproduce? | Verify and test fix | Reproduction steps |
| What's expected? | Know what "fixed" looks like | Expected behavior |
| What's actual? | Confirm the bug exists | Actual behavior, error messages |
| Where might it be? | Focus investigation | Related code paths, stack trace |
| What's the impact? | Prioritize appropriately | Affected users, severity |
| What shouldn't change? | Avoid regressions | Related functionality to preserve |

### Example Context Bundle

```
Bug: Login returns 500 error for emails with plus sign
Reported by: User support ticket #1234
Severity: High (blocks some users from logging in)

Reproduction:
1. Go to https://dev.example.com/login
2. Enter email: test+alias@example.com
3. Enter any password
4. Click login
5. See 500 Internal Server Error

Expected: 401 (invalid credentials) or 200 (if valid)
Actual: 500 Internal Server Error

Error from logs:
```
TypeError: Cannot read property 'toLowerCase' of undefined
    at validateEmail (src/utils/validation.ts:23)
    at loginHandler (src/routes/auth.ts:45)
```

Likely location:
- src/utils/validation.ts - email validation
- src/routes/auth.ts - login handler

Related code context:
- Email validation uses regex, may not handle + correctly
- User lookup uses email as key

Fix constraints:
- Don't change login flow logic
- Don't modify token generation
- Ensure fix handles: plus signs, dots, other valid email chars

Verification:
- test+alias@example.com should work
- Regular emails still work
- Invalid emails still rejected
```

---

## Summary: Role-Specific Context Bundles

| Agent Role | Primary Focus | Key Context Differs In |
|------------|---------------|----------------------|
| Senior Developer | Building new | Codebase patterns, architecture constraints |
| QA Engineer | Validating built | Deployed environment, test data, expected behavior |
| Bug Fixer | Fixing broken | Reproduction steps, error details, minimal scope |

**Implication:** The task system (or runtime orchestrator) should assemble different context bundles per role, not just pass raw ticket data.

---

## Open Questions

1. **Who assembles context bundles?** Runtime orchestrator? Human orchestrator? Hybrid?
2. **Where does context live?** In tickets? Linked docs? Generated on-demand?
3. **How to keep context fresh?** Codebase changes, docs drift, test data expires.
4. **Role-specific MCP tools?** Should different agents have different tool access?
