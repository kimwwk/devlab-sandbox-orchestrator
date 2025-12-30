# Task Hierarchy: Tracking Integration Exploration

## Context

This document explores how task tracking tools (Jira, Linear) could integrate with the Dev Lab workflow, replacing or complementing task-master.

**Previous findings:**
- [spec-kit assessment](./20251226-architecture-task%20hierarchy-speckit.md) - Templates valuable, structure doesn't fit
- [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md) - Separate human and agent layers
- [Helpful Tools](./20251224-helpful-tools-to-leverage.md) - Docker MCP catalog has Linear/Notion MCPs

**Why explore this?**
- Task-master works but lacks visualization for human orchestrator
- Jira/Linear have mature UX (boards, filters, notifications)
- If MCP access is good, agents get same benefits with better human experience

---

## Proposed Workflow

```
Human Orchestrator
        ↓
Write docs (using spec-kit patterns/templates)
        ↓
Documents contain structured info (user stories, acceptance criteria)
        ↓
Extract and sync to Jira/Linear tickets
        ↓
Agent reads via MCP (current task, context, status updates)
```

**Key clarification:** Documents are source of truth. Tickets are synced copies for execution tracking and visualization.

---

## What spec-kit Provides in This Flow

spec-kit's value is **templates that ensure documents contain what's needed for tickets**:

| Template Field | Purpose | Feeds Into |
|----------------|---------|------------|
| User story format | Consistent requirement structure | Ticket description |
| Acceptance criteria | Testable conditions | Ticket acceptance field |
| Dependencies | What must complete first | Ticket links |
| Context/references | Background for implementer | Ticket description or linked docs |

This is not double entry - documents are authored once, ticket creation extracts from them.

---

## What Agents Need from Task Systems

See [Agent Context Requirements](./20251226-architecture-task%20hierarchy-agent%20context%20requirements.md) for detailed breakdown by role.

**Summary:** Different agent roles need different context bundles. The task system (or runtime orchestrator) should assemble role-appropriate context, not just pass raw ticket data.

---

## MCP Exploration Findings (2025-12-26)

Hands-on exploration of both Linear MCP and Jira (Atlassian) MCP.

### Tool Inventory

| Capability | Linear MCP | Jira MCP |
|------------|------------|----------|
| **Total tools** | 25 | 17 |
| **Query issues** | `list_issues` | `searchJiraIssuesUsingJql` |
| **Get single issue** | `get_issue` | `getJiraIssue` |
| **Create/Update** | `create_issue`, `update_issue` | `createJiraIssue`, `editJiraIssue` |
| **Status transitions** | Via `update_issue` (set state) | `transitionJiraIssue` (explicit) |
| **Comments** | `list_comments`, `create_comment` | `addCommentToJiraIssue` |
| **Projects** | `list_projects`, `get_project` | `getVisibleJiraProjects` |
| **Workflow states** | `list_issue_statuses` | `getTransitionsForJiraIssue` |
| **Documentation** | `search_documentation` | `search` (Rovo), `fetch` |

---

### 1. Available Operations - ANSWERED

| Question | Linear | Jira |
|----------|--------|------|
| **Task queries?** | Yes - `list_issues` with rich filters | Yes - JQL (powerful query language) |
| **"Get next task"?** | Filter by `state=Todo` + `assignee=me` | JQL: `status = "To Do" AND assignee = currentUser()` |
| **Filter by status?** | Yes - `state` parameter | Yes - JQL `status` field |
| **Filter by assignee?** | Yes - `assignee` (supports "me") | Yes - JQL `assignee` field |
| **Filter by labels?** | Yes - `label` parameter | Yes - JQL `labels` field |
| **Filter by project?** | Yes - `project` parameter | Yes - JQL `project` field |
| **Filter by parent?** | Yes - `parentId` parameter | Yes - JQL `parent` field |

**Linear filters:** team, state, cycle, label, assignee, delegate (agent), project, parentId, query (search), createdAt, updatedAt

**Jira JQL examples:**
- `project = KAN AND status = "To Do" ORDER BY priority DESC`
- `assignee = currentUser() AND status != Done`
- `parent = KAN-2` (subtasks)

---

### 2. Context Access - ANSWERED

| Question | Linear | Jira |
|----------|--------|------|
| **Description exposed?** | Yes - Markdown, auto-truncated in list (full in get_issue) | Yes - in `fields.description` |
| **Acceptance criteria?** | Part of description (no dedicated field) | Custom field or part of description |
| **Custom fields?** | Labels, links, estimate, dueDate | Yes - `customfield_*` in response |
| **Parent/hierarchy?** | `parentId` for sub-issues | `fields.parent` with summary & status |
| **Linked documents?** | `documents` array, `links` array | `issuelinks`, attachments |
| **Relations/dependencies?** | `blocks`, `blockedBy`, `relatedTo`, `duplicateOf` | `issuelinks` (various link types) |
| **Git branch?** | Yes - `gitBranchName` auto-generated | Via dev panel (not in basic API) |

**Linear issue response includes:**
```json
{
  "id": "...", "identifier": "OUR-3", "title": "...",
  "description": "Full markdown...",
  "status": "Todo", "labels": [], "team": "Our-pot",
  "gitBranchName": "kimsingcanada/our-3-connect-your-tools",
  "relations": { "blocks": [], "blockedBy": [], ... }
}
```

**Jira issue response includes:**
```json
{
  "key": "KAN-3", "fields": {
    "summary": "...", "description": "...",
    "status": { "name": "In Progress" },
    "parent": { "key": "KAN-2", "fields": { "summary": "..." } },
    "issuetype": { "name": "Subtask" },
    "customfield_*": "..."
  }
}
```

---

### 3. Status Updates - ANSWERED

| Question | Linear | Jira |
|----------|--------|------|
| **Update via MCP?** | Yes - `update_issue` with `state` | Yes - `transitionJiraIssue` |
| **Workflow constraints?** | No - can set any state directly | Yes - must use valid transition ID |
| **Get valid transitions?** | `list_issue_statuses` (all states) | `getTransitionsForJiraIssue` (available from current) |
| **Notifications?** | Yes (Linear's built-in) | Yes (Jira's built-in) |

**Linear status update:**
```json
// Simple - just set the state
{ "id": "OUR-3", "state": "In Progress" }
```

**Jira status update:**
```json
// Must get transition ID first, then use it
// Step 1: getTransitionsForJiraIssue → returns available transitions
// Step 2: transitionJiraIssue with transition.id
{ "issueIdOrKey": "KAN-3", "transition": { "id": "41" } }
```

**Jira workflow example (from KAN-3):**
- Idea (id: 11) → To Do (id: 21) → In Progress (id: 31) → Testing (id: 41) → Done (id: 51)

---

### 4. Query Efficiency - ANSWERED

| Question | Linear | Jira |
|----------|--------|------|
| **Server-side filtering?** | Yes - all filters applied server-side | Yes - JQL executed server-side |
| **Pagination?** | `limit` (max 250), `before`/`after` cursors | `maxResults` (max 100), `nextPageToken` |
| **Token efficiency?** | Good - auto-truncates descriptions | Verbose - full nested objects |
| **cloudId required?** | No | Yes - every call needs cloudId |

**Token comparison (rough estimate from responses):**

| Metric | Linear | Jira |
|--------|--------|------|
| Single issue | ~500 tokens | ~1500 tokens |
| List of 5 issues | ~800 tokens | ~2000 tokens |
| Includes metadata bloat | Low | High (avatars, URLs, nested objects) |

Linear auto-truncates: `"description": "... (truncated, use get_issue for full description)"`

---

## Comparison Summary

| Aspect | Linear | Jira | Winner |
|--------|--------|------|--------|
| **Setup simplicity** | Just connect | Need cloudId for every call | Linear |
| **Query language** | Named parameters | JQL (powerful but learning curve) | Tie |
| **Status updates** | Direct state set | Transition-based (2-step) | Linear |
| **Token efficiency** | Auto-truncation, lean responses | Verbose, nested objects | Linear |
| **Hierarchy support** | parentId, sub-issues | Parent field, subtasks, epics | Jira |
| **Custom fields** | Limited (labels, links) | Extensive (customfield_*) | Jira |
| **Workflow flexibility** | Simple (any state) | Enterprise (transition rules) | Depends |
| **Git integration** | Built-in branch names | Requires dev panel setup | Linear |
| **Enterprise features** | Growing | Mature | Jira |

---

## Recommendation

**For Dev Lab Phase 2: Linear MCP**

Rationale:
1. **Simpler agent integration** - No cloudId juggling, direct state updates
2. **Token efficient** - Auto-truncation keeps context window lean
3. **Git-native** - Branch names generated automatically
4. **Good enough hierarchy** - Sub-issues via parentId
5. **Lower friction** - Human orchestrator can use Linear UI, agents use MCP

**When to choose Jira instead:**
- Enterprise environment already using Jira
- Complex workflow rules required (approvals, gates)
- Extensive custom fields needed
- Integration with Confluence/other Atlassian tools

---

## Open Questions - Resolved

### 1. Available Operations
- Does MCP expose task queries (not just CRUD)? **Yes - both have rich query APIs**
- Is there a "get next available task" or equivalent? **Yes - filter by state + assignee**
- Can agent filter by status, assignee, labels? **Yes - both support all these**

### 2. Context Access
- How is task description/acceptance criteria exposed? **In description field (Markdown)**
- Can agent access custom fields? **Linear: limited; Jira: extensive**
- Are linked documents accessible? **Yes - via links/documents arrays**

### 3. Status Updates
- Can agent update ticket status via MCP? **Yes - both support this**
- Are there workflow constraints? **Linear: no; Jira: yes (transitions)**
- Does update trigger notifications? **Yes - both use native notification systems**

### 4. Query Efficiency
- Does agent need to fetch all and filter locally? **No - server-side filtering**
- Token efficiency? **Linear better (auto-truncation); Jira verbose**

---

## Architecture Position

### Adapter Pattern (Deferred)

The [adapter pattern](./20251224-architecture-task%20hierarchy.md) remains conceptually valuable:

```
Human's tool (Jira / Linear / Notion)
         ↓ Adapter
Portable Schema
         ↓ MCP
Agent
```

But for now, direct Jira/Linear MCP may be sufficient. Add adapter when:
- Multiple tools need to be supported
- Switching tools becomes likely
- Custom operations not covered by native MCP

### Task-master Position

If Jira/Linear MCP covers agent needs:
- Task-master becomes redundant for execution tracking
- May still be useful for local/offline development
- Or as fallback when external tools unavailable

---

## Prototype Results (2025-12-26)

Successfully prototyped full agent workflow with Linear MCP.

### Test Issue: OUR-5

**Title:** [Prototype] Implement JWT authentication
**URL:** https://linear.app/our-pot/issue/OUR-5/prototype-implement-jwt-authentication

### Workflow Executed

| Step | Operation | Result |
|------|-----------|--------|
| 1. Query | `list_issues` with `state=Todo` | Found 5 tasks, identified OUR-5 |
| 2. Claim | `update_issue` with `state=In Progress`, `assignee=me` | Status updated, assigned |
| 3. Progress | `create_comment` with progress report | Comment added with checklist |
| 4. Complete | `create_comment` + `update_issue` with `state=Done` | Completion logged, status updated |

### Key Observations

**What worked well:**
- Single call to update status AND assignee simultaneously
- Markdown in comments renders properly (checklists, headers)
- Auto-generated git branch name available immediately
- Clean JSON responses, token-efficient
- No cloudId or extra identifiers needed

**Agent workflow pattern:**
```
1. list_issues(team, state="Todo") → find available work
2. update_issue(id, state="In Progress", assignee="me") → claim task
3. [Agent does work...]
4. create_comment(issueId, body="Progress...") → report status
5. [Agent completes work...]
6. create_comment(issueId, body="Completed...") → final report
7. update_issue(id, state="Done") → mark complete
```

**Comment template for agents:**
```markdown
## Agent Progress Report

**Status:** [In Progress | Blocked | Completed]

### Completed
- [x] Task 1
- [x] Task 2

### In Progress
- [ ] Task 3

### Blockers
[None | Description]

---
*Generated by Dev Lab agent*
```

### Validated Capabilities

| Capability | Status | Notes |
|------------|--------|-------|
| Query by state | ✅ | `state="Todo"` works |
| Query by assignee | ✅ | `assignee="me"` works |
| Update status | ✅ | Direct state name, no lookup needed |
| Assign to self | ✅ | `assignee="me"` works |
| Add comments | ✅ | Markdown supported |
| Get git branch | ✅ | In issue response |
| Relations | ✅ | blocks/blockedBy available |

### Prototype Conclusion

**Linear MCP is ready for Dev Lab integration.** All required agent operations work as expected with minimal friction.

---

## spec-kit → Linear Sync Prototype (2025-12-26)

### Workflow Validation

The proposed workflow **works and makes sense**:

```
Human Orchestrator
        ↓
Write docs (using spec-kit patterns/templates)
        ↓
Documents contain structured info (user stories, acceptance criteria)
        ↓
Extract and sync to Linear tickets (via sync script)
        ↓
Agent reads via MCP (current task, context, status updates)
```

### spec-kit → Linear Mapping

| spec-kit Element | Linear Mapping | Verified |
|------------------|----------------|----------|
| User Story (P1, P2) | Parent Issue with priority | ✅ OUR-6 |
| Task (T007, T008) | Sub-issue with `parentId` | ✅ OUR-7, OUR-8, OUR-9 |
| Priority (P1=Urgent) | Priority field (1-4) | ✅ |
| Acceptance criteria | Description (Gherkin) | ✅ |
| Phase | Labels or description | ✅ |
| [P] marker | Label "parallelizable" | ✅ |

### Created Issues (Prototype)

| Identifier | Title | Type | Parent |
|------------|-------|------|--------|
| OUR-6 | [US1] Login Flow | User Story | - |
| OUR-7 | [T007] Create auth route | Task | OUR-6 |
| OUR-8 | [T008] Implement bcrypt verification | Task | OUR-6 |
| OUR-9 | [T009] Implement JWT generation | Task | OUR-6 |

### Agent Query Pattern

Agent can get tasks for a user story:
```
list_issues(team, parentId="<user-story-id>")
```

Returns all sub-tasks with:
- Task ID and title
- Description with file paths
- Priority inherited from parent
- Git branch name

### Sync Script

Created prototype at: `prototype-speckit-linear/sync_to_linear.py`

**Features:**
- Parses spec-kit tasks.md format
- Extracts phases, user stories, tasks
- Creates Linear issues with hierarchy
- Maps priorities (P1→Urgent, P2→High)
- Supports dry-run mode

**Limitations (fixable):**
- Labels not auto-created (need to pre-create in Linear)
- mcp-cli path issue in subprocess (needs full path or bash wrapper)

### Workflow Verdict: **VALIDATED**

The spec-kit → Linear workflow makes sense because:

1. **Documents remain source of truth** - Human-friendly authoring in markdown
2. **Linear provides visualization** - Boards, filters, progress tracking
3. **Sync is automatable** - Parse markdown, create issues via MCP
4. **Agent reads from Linear** - Gets structured task data with hierarchy
5. **Hierarchy preserved** - User Story → Tasks via parentId

---

## Next Steps

1. ~~**Explore Jira MCP** - Check Docker MCP catalog, understand available operations~~ **DONE**
2. ~~**Explore Linear MCP** - Compare capabilities, may be simpler/better fit~~ **DONE**
3. ~~**Prototype** - Test agent workflow with Linear MCP~~ **DONE**
4. ~~**Prototype** - Test spec-kit → Linear sync~~ **DONE**
5. **Productionize sync script** - Fix mcp-cli path, add error handling
6. **Integrate with Runtime Orchestrator** - Add Linear MCP to agent provisioning
7. **Define conventions** - Document how agents should use Linear (labels, naming, etc.)
8. **Create agent prompt templates** - Include Linear MCP tools in agent prompts

---

## Related Documents

- [Agent Context Requirements](./20251226-architecture-task%20hierarchy-agent%20context%20requirements.md) - Role-specific context needs
- [Task Hierarchy Architecture](./20251224-architecture-task%20hierarchy.md) - Problem definition, layer separation
- [Task Hierarchy Schema](./20251224-architecture-task%20hierarchy-schema.md) - Portable schema exploration
- [spec-kit Assessment](./20251226-architecture-task%20hierarchy-speckit.md) - Template patterns
- [Helpful Tools](./20251224-helpful-tools-to-leverage.md) - Docker MCP catalog
