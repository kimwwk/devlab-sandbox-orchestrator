# Guide: Architecture vs Implementation

## Purpose

This document clarifies what belongs in architecture documentation versus technical design/implementation docs. Getting this wrong causes docs to rot, creates coupling, and makes change painful.

**Related Documents:**
- [ARCHITECTURE_INDEX.md](./ARCHITECTURE_INDEX.md) - System architecture entry point
- [Operating Model: Truth Layers](./20251230-operating-model-truth-layers.md) - Where things live
- [Operating Model: Work Decomposition](./20251230-operating-model-work-decomposition.md) - How work flows

---

## The Core Distinction

| Layer | What It Defines | Lifecycle | Truth Source |
|-------|----------------|-----------|--------------|
| **Architecture** | Constraints, boundaries, invariants | Stable | Docs (ADRs) |
| **Technical Design** | How we plan to implement | Temporary | Doc → becomes history |
| **Implementation** | Actual code, schemas, APIs | Always-current | Code + schema repo |

**Key insight:** Architecture is timeless. Technical design is time-bound. Code is the ultimate truth.

---

## What Architecture Documents

Architecture defines **what must be true** — not how it currently works.

### Architecture Outputs

| Include | Example |
|---------|---------|
| Domain model (conceptual) | "User identity owned by Auth Service" |
| Boundaries | "Payments cannot reference internal athlete IDs" |
| Invariants | "Auth tokens must be stateless and verifiable without DB lookup" |
| Contracts (conceptual) | "Events are published async, never queried synchronously" |
| Trust boundaries | "External API never receives raw database IDs" |
| Consistency guarantees | "Order creation is strongly consistent within region" |
| Non-functional requirements | "P99 latency < 200ms for core read paths" |

### NOT Architecture

| Exclude | Where It Belongs |
|---------|------------------|
| Table schemas / column names | Migration files, schema repo |
| API endpoint routes | OpenAPI specs, code |
| DTO fields / JSON payloads | Code, protobuf/schema files |
| Class diagrams | Technical Design Doc |
| Pseudo-code | Technical Design Doc |
| Sprint scope | Linear / project management |
| UI flows | Product / design docs |
| Performance test plans | Test documentation |

---

## The Technology Choice Problem

### Wrong Approach

```
"We use JWT, PostgreSQL, and React."
```

This is a status report, not architecture. When tech changes, the doc becomes obsolete overnight.

### Correct Approach

```
Constraint: Authentication tokens must be stateless and verifiable without DB lookup.
Current implementation: JWT tokens signed with HS256.

Constraint: Primary persistence must support strong consistency and ACID semantics.
Current implementation: PostgreSQL.
```

The constraint stays true even if technology changes. The implementation note updates.

### When Technology Belongs in Architecture

Only when it's a **strategic, binding decision** — documented as an ADR with trade-offs:

```markdown
# ADR-015: PostgreSQL as System-of-Record Database

## Decision
PostgreSQL is mandated for all core domains.

## Context
Operational maturity, ecosystem alignment, transactional requirements.

## Consequences
- Team must maintain PostgreSQL expertise
- No NoSQL for core domains without new ADR
- Migrations use standard tooling
```

That's a constraint, not a casual bullet point.

---

## Architecture vs Implementation Boundary

| Statement | Type | Belongs In |
|-----------|------|------------|
| "We use X" | Implementation | TDD / README |
| "We must support X property, using Y to satisfy it" | Architecture | SAD / ADR |
| "We will always use Y (strategic decision)" | Architecture Constraint | ADR |

### Litmus Test

If updating the doc requires rewriting huge sections when implementation changes, your architecture isn't modular — you're documenting solutions instead of constraints.

**A good SAD makes change localized.**

---

## Software Architecture Document (SAD) Structure

A constraint-focused SAD that doesn't become a design diary:

### 1. Overview & Scope
- Problem & system context (what this system IS and IS NOT responsible for)
- High-level purpose & value
- Out-of-scope boundaries

### 2. Architecture Principles & Invariants
- Core design principles
- Non-negotiable constraints (security, data ownership, performance)
- Assumptions & guarantees

### 3. System Context & External Dependencies
- Context diagram
- External systems & trust boundaries
- Upstream / downstream contracts

### 4. Domain & Responsibility Decomposition
- Bounded contexts / modules / services
- Responsibilities per component
- **Anti-responsibilities** (what each component must NEVER do)

### 5. Interfaces, Contracts & Data Flows
- Public APIs / events / schemas (conceptual level)
- Data ownership rules
- Sync vs async boundaries

### 6. ADR Index
- List of decisions + links
- Superseded decisions noted
- Open decisions / pending evaluation

### 7. Quality Attributes & Cross-Cutting Concerns
- Reliability, availability, scalability
- Security model
- Observability, logging, auditing
- Performance constraints

### 8. Operational & Deployment View (Conceptual)
- Runtime topology
- Failure / degradation modes
- Recovery & resilience strategy

### 9. Risks, Trade-offs & Known Limitations
- Explicit trade-offs made
- Risks accepted
- Areas intentionally provisional

### 10. Evolution & Change Model
- Rules for introducing new components or boundaries
- When a change requires a new ADR
- What belongs in TDD vs architecture

---

## Technical Design Documents (TDD)

Engineers SHOULD write solution docs with data models & API specs.

### TDD Purpose

- Clarify thinking before implementation
- Align stakeholders
- Reveal risks early
- Make decisions explicit
- Justify trade-offs
- Support reviews
- Create migration plans

### TDD Lifecycle

```
Planning → Implementation → History
   ↓            ↓             ↓
  TDD       Code/Schema    Rationale
(forward)    (truth)      (reference)
```

After implementation, truth moves to code + OpenAPI + migrations. The reasoning remains in the TDD as history.

**Outdated implementation details in architecture = dangerous.**
**Outdated details in a TDD = harmless (served its purpose).**

---

## Promotion Path

When a design decision becomes reusable and invariant:

```
Technical Design Doc → ADR → Architecture
```

### Promotion Triggers

| Trigger | Action |
|---------|--------|
| Decision affects multiple features | Promote to ADR |
| Constraint becomes permanent | Promote to Architecture |
| Pattern becomes standard | Document in SAD |
| One-off implementation choice | Stays in TDD / code |

---

## Conceptual vs Detailed Schemas

### Architecture (Conceptual)

Answers:
- Who owns this data?
- Which system is source of truth?
- What flows across boundaries?
- What guarantees about consistency?
- What is the entity lifecycle?

Example:
```
User identity is owned by Auth Service, not duplicated elsewhere.
TrainingSession belongs to Coaching Domain, not Analytics.
AthleteMetrics events are published async, never queried sync.
```

### Implementation (Detailed)

Lives in:
- Migration files
- OpenAPI / protobuf definitions
- Schema repositories
- Test fixtures
- Typed contracts

Architecture references the source, doesn't duplicate:
```
"See payments_v2.proto for field-level schema."
```

---

## Common Mistakes

### Mistake 1: Technology Shopping Lists

```markdown
## Tech Stack
- Frontend: React
- Backend: Node.js
- Database: PostgreSQL
```

**Problem:** Not architecture. Just current state.

**Fix:** Express as constraints with current implementations.

### Mistake 2: Detailed Schemas in SAD

```markdown
## User Table
| Column | Type | Nullable |
|--------|------|----------|
| id | UUID | No |
| email | VARCHAR(255) | No |
```

**Problem:** Changes constantly. Will rot.

**Fix:** Move to migration files. SAD references: "See `migrations/001_users.sql`"

### Mistake 3: API Payloads in Architecture

```markdown
## Login Response
{
  "token": "string",
  "expiresAt": "ISO8601"
}
```

**Problem:** Implementation detail. Changes with every iteration.

**Fix:** Move to OpenAPI spec. Architecture states: "Login returns stateless token with expiration."

### Mistake 4: Mixing Process with Architecture

```markdown
## Authentication
We use JWT tokens. Sprint 3 will add refresh tokens.
```

**Problem:** Sprint scope in architecture doc.

**Fix:** Architecture describes constraints. Sprint scope lives in Linear.

---

## Summary

| Question | Answer |
|----------|--------|
| What defines architecture? | Constraints, boundaries, invariants |
| What defines implementation? | Code, schemas, APIs |
| Where do tech choices go? | ADR if strategic, otherwise just code |
| When do TDDs become outdated? | After implementation (by design) |
| What's the truth source? | Code + schema, not docs |
| When to update architecture? | When constraints change, not implementations |

---

## Blunt Truth

If your architecture doc lists technologies like a shopping list → you're documenting what exists, not what must remain true.

If updating your SAD requires rewriting huge sections → your architecture isn't modular — decisions are entangled, boundaries are weak.

If you feel the need to document table fields in architecture → you don't trust your boundaries yet.

**Architecture sets the rules of the game.**
**Technical design decides how we play the round.**
**Code is the game itself.**

---

*Last updated: 2025-12-30*
