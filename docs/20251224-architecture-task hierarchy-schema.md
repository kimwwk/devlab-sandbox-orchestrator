# Schema & Workflow Exploration

## Purpose

Explore widely supported schemas and real-world workflows to inform DevLab's task hierarchy design. Goal is to find patterns that:
- Enable future tool swap (not locked in)
- Help human orchestrator plan better
- Work for agent integration
- Align with industry standards

---

## Exploration: Jira Data Model

Jira represents decades of enterprise project management patterns.

```yaml
Epic:
  key: string           # PROJ-123
  summary: string
  description: string   # rich text
  status: string        # To Do, In Progress, Done
  priority: string      # Highest, High, Medium, Low, Lowest
  labels: string[]
  components: string[]
  fix_versions: string[]
  custom_fields: map    # extensibility

Story:
  key: string
  summary: string
  description: string
  status: string
  priority: string
  story_points: number
  acceptance_criteria: string
  parent: Epic.key      # hierarchy link

Task:
  key: string
  summary: string
  description: string
  status: string
  assignee: string
  parent: Story.key or Epic.key
  subtasks: Task[]      # nested hierarchy

Workflow:
  statuses: [To Do, In Progress, In Review, Done]
  transitions: [
    {from: "To Do", to: "In Progress"},
    {from: "In Progress", to: "In Review"},
    {from: "In Review", to: "Done"},
    {from: "In Review", to: "In Progress"},  # rejection loop
  ]
```

**Key patterns from Jira:**
- Hierarchy via `parent` field (not folder nesting)
- Workflow as explicit state machine with transitions
- Custom fields for extension without schema change
- Labels/components for cross-cutting concerns
- Version tracking (fix_versions)

**Considerations:**
- Jira is powerful but complex - do we need all of it?
- Workflow transitions enforce process - good for teams, maybe overkill for solo?
- Custom fields are powerful but can become chaos without governance

---

## Exploration: User Story Format

The standard user story format from Agile:

```
As a [role]
I want [capability]
So that [benefit]
```

**Extended patterns:**
- **INVEST criteria**: Independent, Negotiable, Valuable, Estimable, Small, Testable
- **Priority schemes**: MoSCoW (Must, Should, Could, Won't), numbered (P1, P2, P3)
- **Story points**: Relative effort estimation (Fibonacci: 1, 2, 3, 5, 8, 13)

**Considerations:**
- "As a user" is human-centric - does it work for agent context?
- The format enforces thinking about WHY, not just WHAT
- Keeps scope small and testable

---

## Exploration: Acceptance Criteria (Gherkin/BDD)

Behavior-Driven Development format:

```gherkin
Scenario: User logs in successfully
  Given I am on the login page
  When I enter valid credentials
  And I click the login button
  Then I should be redirected to the dashboard
  And I should see a welcome message

Scenario: User login fails with wrong password
  Given I am on the login page
  When I enter valid email but wrong password
  And I click the login button
  Then I should see an error message "Invalid credentials"
  And I should remain on the login page
```

**Key patterns:**
- **Given** - precondition/context (system state before action)
- **When** - action (what user/system does)
- **Then** - expected outcome (verifiable result)
- **And/But** - additional steps in same category

**Considerations:**
- Very testable - can be automated (Cucumber, Playwright)
- Forces thinking about edge cases
- Can become verbose for simple tasks
- Agents can parse and verify these structured criteria

---

## Exploration: spec-kit Templates

What spec-kit captured in their templates:

### Spec Template
```markdown
# Feature Specification: [NAME]

## User Scenarios (mandatory)
- Prioritized as P1, P2, P3
- Each scenario independently testable
- Each can be MVP increment

### User Story 1 - [Title] (Priority: P1)
[Description in plain language]

**Why this priority**: [Value explanation]
**Independent Test**: [How to verify standalone]

**Acceptance Scenarios**:
1. Given [state], When [action], Then [outcome]

## Requirements (mandatory)
- FR-001: System MUST [capability]
- FR-002: System MUST [capability]

## Key Entities
- [Entity]: [attributes, relationships]

## Success Criteria (mandatory)
- SC-001: [Measurable outcome]
```

### Tasks Template
```markdown
## Phase 1: Setup (Shared Infrastructure)
- [ ] T001 Create project structure
- [ ] T002 [P] Initialize dependencies  # [P] = parallelizable

## Phase 2: Foundational (Blocking)
**CRITICAL**: Blocks all user stories
- [ ] T003 Setup database schema

## Phase 3: User Story 1 (Priority: P1)
**Goal**: [What this delivers]
**Independent Test**: [How to verify]

### Tests (if requested)
- [ ] T004 [P] [US1] Contract test

### Implementation
- [ ] T005 [US1] Create model
- [ ] T006 [US1] Implement service

**Checkpoint**: Story 1 should be independently functional
```

**Key patterns from spec-kit:**
- Phases with explicit dependencies
- Checkpoints for validation
- [P] markers for parallelization
- [US1] markers for traceability to user story
- Tasks include file paths (concrete)

**Considerations:**
- Very detailed task format - good for agents?
- Phase structure enforces order
- Checkpoint concept is valuable - pause and verify
- Traceability markers help navigation

---

## Exploration: Real-World BA Workflow

How Business Analysts actually work:

```
┌─────────────────────────────────────────────────────────────┐
│                    BA WORKFLOW                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Discovery          Analysis           Specification        │
│  ─────────          ────────           ─────────────        │
│  - Stakeholder      - Process          - User Stories       │
│    interviews         mapping          - Acceptance         │
│  - Problem          - Gap analysis       Criteria           │
│    statement        - Feasibility      - Data Model         │
│  - Goals            - Constraints      - UI Wireframes      │
│  - Scope                               - API Contracts      │
│                                                              │
│           ↓                ↓                  ↓              │
│                                                              │
│       Intent.md        TDD.md            SAD.md             │
│       Vision.md                       Feature-vX.md         │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Validation         Handoff            Iteration            │
│  ──────────         ───────            ─────────            │
│  - Review with      - Dev receives     - Feedback from      │
│    stakeholders       spec + context     implementation     │
│  - Acceptance       - Q&A session      - Spec updates       │
│    sign-off         - Definition       - New requirements   │
│  - Scope lock         of Done          - Lessons learned    │
│                                                              │
│           ↓                ↓                  ↓              │
│                                                              │
│    Future-Features.md   (Agent receives)   solutions/       │
│    (out of scope)                          references/      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key BA artifacts:**

| Artifact | Purpose | Maps to |
|----------|---------|---------|
| BRD (Business Requirements) | Why, what problem | Product-Intention.md |
| FRS (Functional Requirements) | What system does | SAD sections |
| Use Cases / User Stories | User perspective | Feature-vX.md |
| Process Flows | How things work | Mermaid diagrams in SAD |
| Data Dictionary | Entities and relationships | SAD Data Layer |
| Wireframes/Mockups | UI expectations | v0 prototype reference |
| Acceptance Criteria | How to verify done | "Done When" sections |

**Considerations:**
- BA workflow has clear phases with handoffs
- Validation before handoff is critical
- Iteration/feedback loop is expected (not waterfall)
- "Definition of Done" is a handoff contract

---

## Exploration: Your Existing Structure

Your folder structure already maps to industry patterns:

```
doc/
├── 20251217-Product-Intention.md      # Discovery → BRD
├── 20251217-TDD-*.md                  # Analysis → ADR
├── 20251218-Product-Vision.md         # Discovery → Product Strategy
├── 20251218-SAD-v1-*.md               # Specification → FRS
├── 20251219-Feature-v1.md             # Specification → User Stories + Tasks
├── 20251221-Feature-v1.1.md           # Iteration → Updated scope
├── 20251221-Future-Features.md        # Validation → Scope lock (out)
├── references/                         # Knowledge base
└── solutions/                          # Iteration → Lessons learned
```

**What's working:**
- Date prefixes provide temporal ordering
- Progressive refinement (Intent → Vision → SAD → Features)
- Explicit scoping (Future-Features = what's out)
- Version tracking (Feature-v1, v1.1)
- Memory system (solutions/)
- References for reusable knowledge

**What could be enhanced:**
- Status tracking (checkboxes are fragile)
- Hierarchy links (implicit in sections, not explicit)
- Acceptance criteria format (varies)
- Agent navigation conventions

---

## Synthesis: A Portable Schema

Goal: Define a schema that maps to multiple tools and formats.

```yaml
# work-item.schema.yaml

WorkItem:
  # Identity
  id: string              # unique identifier (ULID recommended)
  type: enum              # [epic, story, task, subtask]
  title: string           # short summary
  description: string     # markdown content

  # Hierarchy
  parent_id: string?      # link to parent work item

  # Status (workflow)
  status: enum            # [draft, ready, in_progress, in_review, done, deferred]

  # Priority (MoSCoW)
  priority: enum          # [must, should, could, wont]

  # Ownership
  assignee: string?       # who's responsible

  # Acceptance (Gherkin-style)
  acceptance_criteria:
    - scenario: string
      given: string
      when: string
      then: string

  # Verification
  done_when: string[]     # checklist of completion criteria
  testing_approach: string

  # References (links to other docs)
  references:
    - type: enum          # [sad, tdd, solution, external]
      path: string
      section: string?

  # Dependencies
  depends_on: string[]    # IDs this depends on
  blocks: string[]        # IDs this blocks

  # Metadata
  created_at: datetime
  updated_at: datetime
  version: string         # release version (v1, v1.1)

  # Extension
  labels: string[]        # cross-cutting tags
  custom_fields: map      # tool-specific fields
```

---

## Schema Mapping

How the schema maps to different tools/formats:

| Schema Field | Jira | Markdown (your folder) | spec-kit | task-master |
|--------------|------|------------------------|----------|-------------|
| id | Issue Key (PROJ-123) | Section header | Task ID (T001) | Task ID (1.1) |
| type | Issue Type | Implicit (file type) | Template type | - |
| title | Summary | Header text | Title | title field |
| description | Description | Body content | Description | description field |
| parent_id | Parent Link | Implicit nesting | Phase grouping | parent_id |
| status | Workflow Status | Checkbox [x] | - | status field |
| priority | Priority field | Order in doc | P1, P2, P3 | priority field |
| acceptance_criteria | AC field | "Done When" | Given/When/Then | - |
| references | Linked Issues | "SAD References" | - | - |
| depends_on | Issue Links | "Dependencies" | Phase deps | dependencies |
| version | Fix Version | Feature-vX filename | - | - |
| labels | Labels | - | [P], [US1] markers | tags |

---

## Considerations for Final Approach

### 1. Source of Truth Question

**Option A: Schema first, generate markdown**
- Schema (YAML/JSON) is source of truth
- Generate human-readable markdown from schema
- Agents edit schema, humans read markdown
- Pro: Structured, parseable
- Con: Extra step, markdown becomes stale

**Option B: Markdown first, derive schema**
- Markdown is source of truth (your current approach)
- Parse markdown to extract schema when needed
- Pro: Human-friendly authoring
- Con: Parsing is fragile, format must be consistent

**Option C: Bidirectional sync**
- Either can be source of truth
- Sync changes between them
- Pro: Flexibility
- Con: Complexity, conflict resolution

**Current lean:** Option B with conventions. Markdown is natural for humans. Add frontmatter for structured fields. Parse when needed.

### 2. Dynamic Planning Reality

Planning isn't waterfall. Docs evolve. How to handle:

- **Version field** - tracks which release
- **Status workflow** - tracks lifecycle of each item
- **Updated_at** - know what's fresh vs stale
- **Date prefixes** - your current approach works

### 3. Minimal Viable Schema

Start small, extend as needed:

**Must have:**
- id, type, title, status, parent_id
- done_when (acceptance)

**Should have:**
- priority, depends_on, references
- description, testing_approach

**Could have:**
- acceptance_criteria (Gherkin format)
- labels, custom_fields

**Won't have (for now):**
- Story points, time estimates
- Assignee (single orchestrator phase)

### 4. Agent Status Updates

Options for how agent updates status:

| Approach | Mechanism | Pro | Con |
|----------|-----------|-----|-----|
| Edit checkbox in markdown | Search/replace | Simple, human-readable | Fragile parsing |
| Update frontmatter | YAML header | Structured | Less visible to humans |
| Separate status file | status.json | Clean separation | Another file to manage |
| MCP tool | API call | Clean agent interface | Needs implementation |
| task-master | Existing tool | Already works | Separate system |

---

## Open Questions

1. **What's the minimum schema that serves both human planning and agent execution?**

2. **Should we adopt Gherkin for all acceptance criteria, or is "Done When" sufficient?**

3. **How to handle the Feature-vX.md → individual task tracking?**
   - Keep tasks in Feature-vX.md (current)?
   - Extract to separate task files?
   - Use task-master for execution, Feature-vX.md for planning?

4. **What conventions enable agents to navigate your folder structure reliably?**

5. **Is bidirectional sync worth the complexity, or is one source of truth better?**

---

## Next Steps

1. Define minimal schema for DevLab
2. Document conventions for agent navigation
3. Consider adapter pattern for tool portability
4. Prototype: parse existing Feature-v1.md into schema
5. Validate: does schema capture what agents need?
