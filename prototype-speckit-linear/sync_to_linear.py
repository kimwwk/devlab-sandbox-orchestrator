#!/usr/bin/env python3
"""
Prototype: spec-kit tasks.md → Linear sync

This script demonstrates parsing spec-kit tasks.md format
and creating corresponding Linear issues via MCP CLI.

Usage:
    python sync_to_linear.py sample-tasks.md --team "Our-pot" --dry-run
    python sync_to_linear.py sample-tasks.md --team "Our-pot"
"""

import re
import json
import subprocess
import argparse
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    id: str                          # T001, T002, etc.
    title: str                       # Task description
    phase: str                       # "Setup", "Foundational", "User Story 1"
    phase_num: int                   # 1, 2, 3...
    user_story: Optional[str] = None # US1, US2, etc.
    parallelizable: bool = False     # [P] marker
    priority: int = 3                # 1=Urgent, 2=High, 3=Normal, 4=Low


@dataclass
class UserStory:
    id: str                          # US1, US2
    title: str                       # "Login Flow"
    priority: str                    # P1, P2
    goal: str                        # Goal description
    acceptance: list[str] = field(default_factory=list)  # Given/When/Then scenarios
    tasks: list[Task] = field(default_factory=list)


@dataclass
class ParsedSpec:
    feature_name: str
    phases: dict[str, list[Task]]    # phase_name -> tasks
    user_stories: dict[str, UserStory]  # US1 -> UserStory


def parse_tasks_md(content: str) -> ParsedSpec:
    """Parse spec-kit tasks.md format."""

    lines = content.split('\n')

    # Extract feature name from title
    feature_match = re.search(r'^# Tasks: (.+)$', content, re.MULTILINE)
    feature_name = feature_match.group(1) if feature_match else "Unknown Feature"

    phases = {}
    user_stories = {}
    current_phase = None
    current_phase_num = 0
    current_story = None
    current_goal = None
    acceptance_scenarios = []

    for line in lines:
        line = line.rstrip()

        # Detect phase headers: ## Phase N: Name
        phase_match = re.match(r'^## Phase (\d+): (.+?)(?:\s*\(Priority: (P\d)\))?$', line)
        if phase_match:
            current_phase_num = int(phase_match.group(1))
            phase_name = phase_match.group(2).strip()
            priority = phase_match.group(3)
            current_phase = phase_name

            if phase_name not in phases:
                phases[phase_name] = []

            # Check if this is a User Story phase
            story_match = re.match(r'User Story (\d+) - (.+)', phase_name)
            if story_match:
                story_num = story_match.group(1)
                story_title = story_match.group(2)
                current_story = f"US{story_num}"

                # Map P1 -> priority 1 (Urgent), P2 -> priority 2 (High), etc.
                linear_priority = int(priority[1]) if priority else 3

                user_stories[current_story] = UserStory(
                    id=current_story,
                    title=story_title,
                    priority=priority or "P3",
                    goal="",
                    acceptance=[],
                    tasks=[]
                )
            else:
                current_story = None
            continue

        # Detect Goal
        if line.startswith('**Goal**:'):
            goal = line.replace('**Goal**:', '').strip()
            if current_story and current_story in user_stories:
                user_stories[current_story].goal = goal
            continue

        # Detect acceptance scenarios
        if '**Given**' in line and '**When**' in line and '**Then**' in line:
            if current_story and current_story in user_stories:
                user_stories[current_story].acceptance.append(line.strip())
            continue

        # Detect tasks: - [ ] TXXX ...
        task_match = re.match(r'^- \[ \] (T\d+)\s*(.*)$', line)
        if task_match:
            task_id = task_match.group(1)
            task_rest = task_match.group(2)

            # Check for [P] marker
            parallelizable = '[P]' in task_rest
            task_rest = task_rest.replace('[P]', '').strip()

            # Check for [USx] marker
            us_match = re.search(r'\[(US\d+)\]', task_rest)
            task_us = us_match.group(1) if us_match else current_story
            if us_match:
                task_rest = task_rest.replace(f'[{us_match.group(1)}]', '').strip()

            # Map priority: Phase 1-2 = Normal (3), User Stories use their priority
            if current_story and current_story in user_stories:
                priority_str = user_stories[current_story].priority
                linear_priority = int(priority_str[1]) if priority_str else 3
            else:
                linear_priority = 3  # Normal for setup/foundational

            task = Task(
                id=task_id,
                title=task_rest,
                phase=current_phase or "Unknown",
                phase_num=current_phase_num,
                user_story=task_us,
                parallelizable=parallelizable,
                priority=linear_priority
            )

            if current_phase:
                phases[current_phase].append(task)

            if task_us and task_us in user_stories:
                user_stories[task_us].tasks.append(task)

    return ParsedSpec(
        feature_name=feature_name,
        phases=phases,
        user_stories=user_stories
    )


def create_linear_issue(team: str, title: str, description: str,
                        priority: int = 3, labels: list[str] = None,
                        parent_id: str = None, dry_run: bool = False) -> Optional[str]:
    """Create a Linear issue via MCP CLI."""

    params = {
        "team": team,
        "title": title,
        "description": description,
    }

    if priority:
        params["priority"] = priority
    if labels:
        params["labels"] = labels
    if parent_id:
        params["parentId"] = parent_id

    cmd = ["mcp-cli", "call", "linear-server/create_issue", json.dumps(params)]

    if dry_run:
        print(f"[DRY RUN] Would create: {title}")
        print(f"          Priority: {priority}, Labels: {labels}, Parent: {parent_id}")
        return None

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        issue_id = response.get("id")
        identifier = response.get("identifier")
        print(f"Created: {identifier} - {title}")
        return issue_id
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing response")
        return None


def sync_to_linear(spec: ParsedSpec, team: str, dry_run: bool = False):
    """Sync parsed spec to Linear issues."""

    print(f"\n{'='*60}")
    print(f"Syncing: {spec.feature_name}")
    print(f"Team: {team}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    # Track created story IDs for linking tasks
    story_issue_ids = {}

    # 1. Create User Story issues (as parents)
    print("--- Creating User Stories ---")
    for story_id, story in spec.user_stories.items():
        # Build description with acceptance criteria
        description = f"## Goal\n{story.goal}\n\n"
        if story.acceptance:
            description += "## Acceptance Criteria\n"
            for scenario in story.acceptance:
                description += f"- {scenario}\n"

        # Priority mapping: P1->1 (Urgent), P2->2 (High), P3->3 (Normal)
        priority = int(story.priority[1]) if story.priority else 3

        labels = [f"priority:{story.priority}", "user-story"]

        issue_id = create_linear_issue(
            team=team,
            title=f"[{story_id}] {story.title}",
            description=description,
            priority=priority,
            labels=labels,
            dry_run=dry_run
        )

        if issue_id:
            story_issue_ids[story_id] = issue_id

    print("\n--- Creating Tasks ---")

    # 2. Create tasks (linked to user stories if applicable)
    for phase_name, tasks in spec.phases.items():
        print(f"\nPhase: {phase_name}")

        for task in tasks:
            labels = [f"phase:{task.phase_num}"]
            if task.parallelizable:
                labels.append("parallelizable")

            parent_id = None
            if task.user_story and task.user_story in story_issue_ids:
                parent_id = story_issue_ids[task.user_story]

            create_linear_issue(
                team=team,
                title=f"[{task.id}] {task.title}",
                description=f"Phase: {phase_name}\nParallelizable: {task.parallelizable}",
                priority=task.priority,
                labels=labels,
                parent_id=parent_id,
                dry_run=dry_run
            )

    print(f"\n{'='*60}")
    print("Sync complete!")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Sync spec-kit tasks.md to Linear')
    parser.add_argument('file', help='Path to tasks.md file')
    parser.add_argument('--team', required=True, help='Linear team name')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating')

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        content = f.read()

    spec = parse_tasks_md(content)

    # Debug: show parsed structure
    print(f"Parsed feature: {spec.feature_name}")
    print(f"Phases: {list(spec.phases.keys())}")
    print(f"User Stories: {list(spec.user_stories.keys())}")
    for story_id, story in spec.user_stories.items():
        print(f"  {story_id}: {story.title} ({story.priority}) - {len(story.tasks)} tasks")

    sync_to_linear(spec, args.team, args.dry_run)


if __name__ == "__main__":
    main()
