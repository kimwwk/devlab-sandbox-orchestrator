"""Shared prompt fragments used across agent roles."""

REPORT_INSTRUCTION = """

<completion-report>
When you finish, end with a brief completion report in this exact format:

## Status
DONE or BLOCKED (one word)

## What Changed
- List each file changed and what was done (1 line per file)

## Key Decisions
- Any non-obvious choices you made and why (skip if none)

## PR / Branch
- Branch name and PR link if created (skip if none)

Keep the report concise — a few bullet points, not paragraphs.
</completion-report>
"""

LINEAR_CONTEXT = """Task Management: Linear (accessed via MCP tools)
Issue: {issue_id}"""

LINEAR_FETCH_HINT = "Start by using the get_issue MCP tool to retrieve the full issue details{details_suffix}"

LINEAR_FETCH_HINT_DEV = LINEAR_FETCH_HINT.format(
    details_suffix=" — title, description, and acceptance criteria. This is your source of truth for what needs to be done."
)

LINEAR_FETCH_HINT_QA = LINEAR_FETCH_HINT.format(
    details_suffix=". Understand what was implemented and what the acceptance criteria are."
)
