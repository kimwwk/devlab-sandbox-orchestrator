"""Tests for the prompts module."""

import pytest
from devlab.prompts import compose_prompt
from devlab.prompts import developer, dev_lead, qa, qa_lead, reviewer, analyst
from devlab.prompts._common import REPORT_INSTRUCTION


class TestComposePromptRouting:
    """compose_prompt dispatches to the correct role module."""

    def test_routes_to_developer(self):
        result = compose_prompt("do something", "developer")
        assert "senior developer" in result

    def test_routes_to_qa(self):
        result = compose_prompt("test something", "qa")
        assert "QA engineer" in result

    def test_routes_to_reviewer(self):
        result = compose_prompt("review this", "reviewer")
        assert "code reviewer" in result

    def test_routes_to_analyst(self):
        result = compose_prompt("analyze this", "analyst")
        assert "research analyst" in result

    def test_defaults_to_developer(self):
        result = compose_prompt("do something")
        assert "senior developer" in result

    def test_routes_to_dev_lead(self):
        result = compose_prompt("do something", "dev-lead")
        assert "dev lead" in result

    def test_routes_to_qa_lead(self):
        result = compose_prompt("test something", "qa-lead")
        assert "QA lead" in result

    def test_unknown_role_falls_back_to_developer(self):
        result = compose_prompt("do something", "unknown_role")
        assert "senior developer" in result


class TestReportInstruction:
    """All roles append the completion report."""

    @pytest.mark.parametrize("role", ["developer", "dev-lead", "qa", "qa-lead", "reviewer", "analyst"])
    def test_report_appended_direct(self, role):
        result = compose_prompt("task", role, source="direct")
        assert "<completion-report>" in result
        assert "DONE or BLOCKED" in result

    @pytest.mark.parametrize("role", ["developer", "dev-lead", "qa", "qa-lead"])
    def test_report_appended_linear(self, role):
        result = compose_prompt("OUR-5", role, source="linear")
        assert "<completion-report>" in result


class TestDeveloperPrompts:

    def test_direct_includes_task(self):
        result = developer.compose_prompt("Fix the login bug", source="direct")
        assert "Fix the login bug" in result

    def test_direct_has_role_section(self):
        result = developer.compose_prompt("task", source="direct")
        assert "<your-role>" in result
        assert "</your-role>" in result

    def test_direct_has_task_section(self):
        result = developer.compose_prompt("my task", source="direct")
        assert "<task-instructions>" in result
        assert "my task" in result

    def test_direct_has_soft_guidance(self):
        result = developer.compose_prompt("task", source="direct")
        assert "<soft-guidance>" in result

    def test_linear_includes_issue_id(self):
        result = developer.compose_prompt("OUR-42", source="linear")
        assert "OUR-42" in result

    def test_linear_has_linear_context(self):
        result = developer.compose_prompt("OUR-42", source="linear")
        assert "Linear" in result
        assert "get_issue MCP tool" in result

    def test_linear_has_feature_branch_guidance(self):
        result = developer.compose_prompt("OUR-42", source="linear")
        assert "feature/" in result

    def test_linear_has_state_transitions(self):
        result = developer.compose_prompt("OUR-42", source="linear")
        assert "Dev in Progress" in result
        assert "Test in Progress" in result


class TestQAPrompts:

    def test_direct_includes_task(self):
        result = qa.compose_prompt("Run regression tests", source="direct")
        assert "Run regression tests" in result

    def test_direct_has_qa_identity(self):
        result = qa.compose_prompt("task", source="direct")
        assert "QA engineer" in result
        assert "How might this break?" in result

    def test_direct_does_not_have_linear_context(self):
        result = qa.compose_prompt("task", source="direct")
        assert "Linear" not in result

    def test_linear_includes_issue_id(self):
        result = qa.compose_prompt("OUR-10", source="linear")
        assert "OUR-10" in result

    def test_linear_has_test_tiers(self):
        result = qa.compose_prompt("OUR-10", source="linear")
        assert "smoke" in result
        assert "regression" in result

    def test_linear_has_state_transitions(self):
        result = qa.compose_prompt("OUR-10", source="linear")
        assert "Done" in result
        assert "Dev in Progress" in result


class TestDevLeadPrompts:

    def test_direct_includes_task(self):
        result = dev_lead.compose_prompt("Refactor the auth module", source="direct")
        assert "Refactor the auth module" in result

    def test_direct_has_architectural_perspective(self):
        result = dev_lead.compose_prompt("task", source="direct")
        assert "architect" in result
        assert "design" in result.lower()

    def test_direct_has_holistic_context(self):
        result = dev_lead.compose_prompt("task", source="direct")
        assert "folder structure" in result
        assert "module boundaries" in result

    def test_direct_has_design_first_guidance(self):
        result = dev_lead.compose_prompt("task", source="direct")
        assert "Design before you build" in result

    def test_linear_includes_issue_id(self):
        result = dev_lead.compose_prompt("OUR-99", source="linear")
        assert "OUR-99" in result

    def test_linear_has_linear_context(self):
        result = dev_lead.compose_prompt("OUR-99", source="linear")
        assert "Linear" in result
        assert "get_issue MCP tool" in result

    def test_linear_has_state_transitions(self):
        result = dev_lead.compose_prompt("OUR-99", source="linear")
        assert "Dev in Progress" in result
        assert "Test in Progress" in result

    def test_linear_has_architecture_label_guidance(self):
        result = dev_lead.compose_prompt("OUR-99", source="linear")
        assert "architecture" in result


class TestQALeadPrompts:

    def test_direct_includes_task(self):
        result = qa_lead.compose_prompt("Set up E2E tests", source="direct")
        assert "Set up E2E tests" in result

    def test_direct_has_strategic_perspective(self):
        result = qa_lead.compose_prompt("task", source="direct")
        assert "QA lead" in result
        assert "test strategy" in result

    def test_direct_has_infrastructure_thinking(self):
        result = qa_lead.compose_prompt("task", source="direct")
        assert "test architecture" in result
        assert "shared helpers" in result

    def test_direct_has_design_first_guidance(self):
        result = qa_lead.compose_prompt("task", source="direct")
        assert "Design the test approach" in result

    def test_direct_does_not_have_linear_context(self):
        result = qa_lead.compose_prompt("task", source="direct")
        assert "Linear" not in result

    def test_linear_includes_issue_id(self):
        result = qa_lead.compose_prompt("OUR-77", source="linear")
        assert "OUR-77" in result

    def test_linear_has_test_tiers(self):
        result = qa_lead.compose_prompt("OUR-77", source="linear")
        assert "smoke" in result
        assert "regression" in result

    def test_linear_has_state_transitions(self):
        result = qa_lead.compose_prompt("OUR-77", source="linear")
        assert "Done" in result
        assert "Dev in Progress" in result


class TestReviewerPrompts:

    def test_includes_task(self):
        result = reviewer.compose_prompt("Review PR #42", source="direct")
        assert "Review PR #42" in result

    def test_has_reviewer_identity(self):
        result = reviewer.compose_prompt("task", source="direct")
        assert "code reviewer" in result

    def test_no_code_changes_constraint(self):
        result = reviewer.compose_prompt("task", source="direct")
        assert "Do not make code changes" in result

    def test_linear_source_same_as_direct(self):
        """Reviewer doesn't have a separate Linear path."""
        direct = reviewer.compose_prompt("task", source="direct")
        linear = reviewer.compose_prompt("task", source="linear")
        assert direct == linear


class TestAnalystPrompts:

    def test_includes_task(self):
        result = analyst.compose_prompt("Analyze the auth flow", source="direct")
        assert "Analyze the auth flow" in result

    def test_has_analyst_identity(self):
        result = analyst.compose_prompt("task", source="direct")
        assert "research analyst" in result

    def test_no_code_modification_constraint(self):
        result = analyst.compose_prompt("task", source="direct")
        assert "Do not modify code files" in result

    def test_linear_source_same_as_direct(self):
        """Analyst doesn't have a separate Linear path."""
        direct = analyst.compose_prompt("task", source="direct")
        linear = analyst.compose_prompt("task", source="linear")
        assert direct == linear


class TestPromptStructure:
    """All prompts follow the expected structure."""

    @pytest.mark.parametrize("role", ["developer", "dev-lead", "qa", "qa-lead", "reviewer", "analyst"])
    def test_has_role_section(self, role):
        result = compose_prompt("task", role)
        assert "<your-role>" in result
        assert "</your-role>" in result

    @pytest.mark.parametrize("role", ["developer", "dev-lead", "qa", "qa-lead", "reviewer", "analyst"])
    def test_has_task_section(self, role):
        result = compose_prompt("task", role)
        assert "<task-instructions>" in result
        assert "</task-instructions>" in result

    @pytest.mark.parametrize("role", ["developer", "dev-lead", "qa", "qa-lead", "reviewer", "analyst"])
    def test_has_soft_guidance(self, role):
        result = compose_prompt("task", role)
        assert "<soft-guidance>" in result
        assert "</soft-guidance>" in result


class TestOrchestratorIntegration:
    """Test compose_task_prompt from orchestrator."""

    def test_linear_issue_config(self):
        from devlab.orchestrator import compose_task_prompt
        config = {"agent": "developer", "linear_issue": "OUR-5"}
        result = compose_task_prompt(config)
        assert "OUR-5" in result
        assert "senior developer" in result
        assert "<completion-report>" in result

    def test_direct_task_config(self):
        from devlab.orchestrator import compose_task_prompt
        config = {"agent": "qa", "task": "Run all smoke tests"}
        result = compose_task_prompt(config)
        assert "Run all smoke tests" in result
        assert "QA engineer" in result
        assert "<completion-report>" in result

    def test_default_agent_is_developer(self):
        from devlab.orchestrator import compose_task_prompt
        config = {"task": "Fix a bug"}
        result = compose_task_prompt(config)
        assert "senior developer" in result
