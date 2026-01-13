# Architecture Index

Canonical entry point to the system’s architectural constraints, decisions, and boundaries.

This document contains **no implementation detail** and **no process guidance**.
It exists solely to route readers to architectural truth.

---

## Core Invariants (Non-Negotiable)

Violating any invariant requires a new ADR.

| ID | Invariant | Canonical Source |
|----|----------|------------------|
| INV-001 | [Invariant statement] | ADR-00X |
| INV-002 | [Invariant statement] | ADR-00Y |
| INV-003 | [Invariant statement] | ADR-00Z |

---

## Architecture Principles

System-level design principles. These guide decisions but do not override invariants.

| ID | Principle | Source |
|----|----------|--------|
| PR-001 | [Principle] | ADR-01X |
| PR-002 | [Principle] | ADR-01Y |

---

## Active Architectural Axes

Current decision domains with accepted canonical ADRs.

| Axis | Canonical ADR | Status |
|-----|--------------|--------|
| Authentication | ADR-010 | Active |
| Data Mutation Model | ADR-012 | Active |
| API Boundaries | ADR-015 | Active |
| AI Integration | ADR-020 | Active |

---

## System Maps

High-level system understanding.

- System Context — `system-maps/context.md`
- Domain Boundaries — `system-maps/domains.md`
- Data Flow — `system-maps/data-flow.md`

---

## Architecture Decision Register

All architectural decisions live in `/adr`.

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | [Title] | Accepted |
| ADR-002 | [Title] | Accepted |
| ADR-003 | [Title] | Draft |

---

## Intent vs Architecture vs Execution

| Layer | Purpose | Location |
|------|--------|----------|
| Intent | Why we are building | `/intent` |
| Architecture | Constraints & decisions | `/adr`, this index |
| Execution | Tasks & status | Linear |

See: `operating-model/truth-layers.md`

---

_Last updated: YYYY-MM-DD_
