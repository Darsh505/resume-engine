"""
test_filter_engine.py — Pytest suite for filter_engine.py.

Coverage
────────
§ filter_list / _matches
§ rank_by_relevance (relevance + priority)
§ apply_budget
§ filter_experience  (regression: zero-bullet jobs are dropped)
§ filter_education   (degree always kept; coursework filtered/budgeted)
§ filter_skills      (empty categories omitted)
§ collect_all_tags   ("general" excluded)
§ build_resume_data  (full integration via tmp YAML fixture)
§ Edge cases         (empty lists, missing "tags", unknown target)
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Items under test (imported at module level so errors surface immediately)
# ---------------------------------------------------------------------------
from filter_engine import (
    _matches,
    _relevance_score,
    apply_budget,
    build_resume_data,
    collect_all_tags,
    filter_education,
    filter_experience,
    filter_list,
    filter_skills,
    rank_by_relevance,
    MAX_BULLETS_PER_JOB,
    MAX_COURSEWORK,
)


# ===========================================================================
# § filter_list / _matches
# ===========================================================================

class TestMatches:
    def test_item_with_target_tag(self):
        item = {"text": "x", "tags": ["backend"]}
        assert _matches(item, "backend") is True

    def test_item_with_only_general_tag(self):
        item = {"text": "x", "tags": ["general"]}
        assert _matches(item, "backend") is True

    def test_item_with_neither_tag(self):
        item = {"text": "x", "tags": ["frontend"]}
        assert _matches(item, "backend") is False

    def test_item_tagged_for_different_target(self):
        item = {"text": "x", "tags": ["data-science", "devops"]}
        assert _matches(item, "backend") is False

    def test_item_missing_tags_key(self):
        """Items without a 'tags' key must not crash; they never match."""
        item = {"text": "no tags here"}
        assert _matches(item, "backend") is False


class TestFilterList:
    def test_keeps_target_tagged_items(self):
        items = [
            {"name": "keep", "tags": ["backend"]},
            {"name": "drop", "tags": ["frontend"]},
            {"name": "also_keep", "tags": ["general"]},
        ]
        result = filter_list(items, "backend")
        assert len(result) == 2
        assert result[0]["name"] == "keep"
        assert result[1]["name"] == "also_keep"

    def test_empty_list_returns_empty(self):
        assert filter_list([], "backend") == []

    def test_unknown_target_returns_only_general(self):
        items = [
            {"name": "g", "tags": ["general"]},
            {"name": "b", "tags": ["backend"]},
        ]
        result = filter_list(items, "mobile")
        assert len(result) == 1
        assert result[0]["name"] == "g"


# ===========================================================================
# § rank_by_relevance
# ===========================================================================

class TestRankByRelevance:
    def test_descending_order(self):
        """Higher relevance score (more tag occurrences) sorts first."""
        items = [
            {"name": "low",  "tags": ["backend"]},
            {"name": "high", "tags": ["backend", "backend"]},
            {"name": "mid",  "tags": ["backend", "general"]},
        ]
        ranked = rank_by_relevance(items, "backend")
        assert ranked[0]["name"] == "high"   # score 2
        assert ranked[1]["name"] == "low"    # score 1 (mid has score 1 too but was after)
        # mid and low both score 1; original order (low before mid in input) preserved
        assert ranked[2]["name"] == "mid"

    def test_stable_order_for_equal_scores(self):
        """Items with identical score preserve their original (YAML) order."""
        items = [
            {"name": "alpha", "tags": ["backend"]},
            {"name": "beta",  "tags": ["backend"]},
            {"name": "gamma", "tags": ["backend"]},
        ]
        ranked = rank_by_relevance(items, "backend")
        assert [i["name"] for i in ranked] == ["alpha", "beta", "gamma"]

    def test_priority_overrides_relevance(self):
        """priority field takes precedence over tag count."""
        items = [
            {"name": "low_prio_high_rel",  "tags": ["backend", "backend"], "priority": 0},
            {"name": "high_prio_low_rel",  "tags": ["backend"],            "priority": 2},
        ]
        ranked = rank_by_relevance(items, "backend")
        assert ranked[0]["name"] == "high_prio_low_rel"
        assert ranked[1]["name"] == "low_prio_high_rel"

    def test_missing_priority_defaults_to_zero(self):
        """Items without a 'priority' key behave as if priority=0."""
        items = [
            {"name": "no_priority", "tags": ["backend"]},
            {"name": "explicit_zero", "tags": ["backend"], "priority": 0},
        ]
        # Both effectively priority=0, so original order is preserved
        ranked = rank_by_relevance(items, "backend")
        assert ranked[0]["name"] == "no_priority"
        assert ranked[1]["name"] == "explicit_zero"

    def test_priority_stable_within_same_priority_and_score(self):
        """Equal priority AND equal score → original order preserved."""
        items = [
            {"name": "a", "tags": ["backend"], "priority": 1},
            {"name": "b", "tags": ["backend"], "priority": 1},
            {"name": "c", "tags": ["backend"], "priority": 1},
        ]
        ranked = rank_by_relevance(items, "backend")
        assert [i["name"] for i in ranked] == ["a", "b", "c"]


# ===========================================================================
# § apply_budget
# ===========================================================================

class TestApplyBudget:
    def test_trims_to_max_n(self):
        items = [{"n": i} for i in range(10)]
        assert apply_budget(items, 3) == items[:3]

    def test_noop_when_under_budget(self):
        items = [{"n": i} for i in range(2)]
        assert apply_budget(items, 5) == items

    def test_noop_when_exactly_at_budget(self):
        items = [{"n": i} for i in range(4)]
        assert apply_budget(items, 4) == items

    def test_empty_list(self):
        assert apply_budget([], 3) == []


# ===========================================================================
# § filter_experience
# ===========================================================================

class TestFilterExperience:
    def test_regression_zero_bullet_job_is_dropped(self, sample_data):
        """
        Regression test — lock in the intentional behavior:
        a job whose bullets ALL fail the tag filter is removed entirely.
        'Irrelevant Co' has only a [frontend] bullet; it must vanish for target=backend.
        """
        experience = sample_data["experience"]
        result = filter_experience(experience, "backend")
        companies = [j["company"] for j in result]
        assert "Irrelevant Co" not in companies

    def test_surviving_bullets_are_capped(self, sample_data):
        """Bullet count per job must not exceed MAX_BULLETS_PER_JOB."""
        experience = sample_data["experience"]
        result = filter_experience(experience, "backend")
        for job in result:
            assert len(job["bullets"]) <= MAX_BULLETS_PER_JOB

    def test_relevant_jobs_are_kept(self, sample_data):
        """Acme Corp has backend bullets → must be kept."""
        result = filter_experience(sample_data["experience"], "backend")
        companies = [j["company"] for j in result]
        assert "Acme Corp" in companies

    def test_original_job_not_mutated(self, sample_data):
        """filter_experience must not mutate the input list (uses deepcopy)."""
        experience = sample_data["experience"]
        original_bullet_count = len(experience[0]["bullets"])
        filter_experience(experience, "backend")
        assert len(experience[0]["bullets"]) == original_bullet_count

    def test_empty_experience_list(self):
        assert filter_experience([], "backend") == []

    def test_unknown_target_only_general_bullets_survive(self, sample_data):
        """For an unknown target, only 'general'-tagged bullets survive."""
        result = filter_experience(sample_data["experience"], "mobile")
        # Acme Corp has 2 general bullets → job survives
        companies = [j["company"] for j in result]
        assert "Acme Corp" in companies
        # 'Irrelevant Co' and 'Old Startup' have no general bullets → dropped
        assert "Old Startup" not in companies
        assert "Irrelevant Co" not in companies


# ===========================================================================
# § filter_education
# ===========================================================================

class TestFilterEducation:
    def test_degree_always_kept_even_with_zero_coursework(self):
        """
        Education entries are always included regardless of coursework count.
        Even when NO coursework matches the target, the degree entry stays.
        """
        education = [
            {
                "institution": "University",
                "degree": "B.S.",
                "dates": "2018–2022",
                "coursework": [
                    {"name": "Frontend course", "tags": ["frontend"]},
                ],
            }
        ]
        result = filter_education(education, "backend")
        assert len(result) == 1
        assert result[0]["institution"] == "University"
        assert result[0]["coursework"] == []

    def test_coursework_is_filtered(self, sample_data):
        """Only coursework matching the target (or 'general') survives."""
        result = filter_education(sample_data["education"], "frontend")
        assert len(result) == 1
        course_names = [c["name"] for c in result[0]["coursework"]]
        # "Web Technologies" (frontend) and "Data Structures" (general) should survive
        assert "Web Technologies" in course_names
        assert "Data Structures" in course_names
        # ML is data-science only → must be absent
        assert "Machine Learning" not in course_names

    def test_coursework_is_budgeted(self, sample_data):
        """Coursework is capped at MAX_COURSEWORK per degree."""
        result = filter_education(sample_data["education"], "backend")
        for entry in result:
            assert len(entry["coursework"]) <= MAX_COURSEWORK

    def test_empty_education_list(self):
        assert filter_education([], "backend") == []


# ===========================================================================
# § filter_skills
# ===========================================================================

class TestFilterSkills:
    def test_empty_categories_omitted(self, sample_data):
        """
        'devops_tools' category in sample_data has only frontend-tagged items.
        For target=backend it must be entirely absent from the output dict.
        """
        result = filter_skills(sample_data["skills"], "backend")
        assert "devops_tools" not in result

    def test_matching_categories_included(self, sample_data):
        result = filter_skills(sample_data["skills"], "backend")
        # 'languages' and 'frameworks' both have backend items
        assert "languages" in result
        assert "frameworks" in result

    def test_skills_are_name_strings_not_dicts(self, sample_data):
        """Output values must be lists of plain strings, not dicts."""
        result = filter_skills(sample_data["skills"], "backend")
        for names in result.values():
            for name in names:
                assert isinstance(name, str)

    def test_empty_skills_dict(self):
        assert filter_skills({}, "backend") == {}

    def test_unknown_target_only_general_categories_survive(self, sample_data):
        """For mobile target, only 'general'-tagged skills remain."""
        result = filter_skills(sample_data["skills"], "mobile")
        # Python, SQL are general → languages survives
        assert "languages" in result
        # frameworks has no general items → absent
        assert "frameworks" not in result


# ===========================================================================
# § collect_all_tags
# ===========================================================================

class TestCollectAllTags:
    def test_general_excluded(self, sample_data):
        tags = collect_all_tags(sample_data)
        assert "general" not in tags

    def test_returns_sorted_list(self, sample_data):
        tags = collect_all_tags(sample_data)
        assert tags == sorted(tags)

    def test_known_tags_present(self, sample_data):
        tags = collect_all_tags(sample_data)
        for expected in ("backend", "frontend", "data-science", "devops"):
            assert expected in tags

    def test_deduplication(self):
        """The same tag appearing many times returns only once."""
        data = {
            "items": [
                {"tags": ["backend"]},
                {"tags": ["backend"]},
                {"tags": ["backend"]},
            ]
        }
        tags = collect_all_tags(data)
        assert tags.count("backend") == 1

    def test_empty_data(self):
        assert collect_all_tags({}) == []


# ===========================================================================
# § build_resume_data  (integration)
# ===========================================================================

class TestBuildResumeData:
    def test_full_integration(self, tmp_yaml):
        """Full pipeline against the fixture YAML — verifies structure and types."""
        result = build_resume_data(tmp_yaml, "backend")

        assert "personal" in result
        assert "education" in result
        assert "experience" in result
        assert "projects" in result
        assert "skills" in result
        assert "achievements" in result
        assert result["target"] == "backend"

        # Every job that survived has at least one bullet
        for job in result["experience"]:
            assert len(job["bullets"]) >= 1

        # Skills values are lists of strings
        for names in result["skills"].values():
            assert all(isinstance(n, str) for n in names)

    def test_empty_top_level_lists(self, tmp_path):
        """All top-level lists empty → build_resume_data must not raise."""
        import yaml

        empty_data = {
            "personal": {"name": "Nobody"},
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {},
            "achievements": [],
        }
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text(yaml.dump(empty_data), encoding="utf-8")

        result = build_resume_data(str(yaml_file), "backend")
        assert result["experience"] == []
        assert result["projects"] == []
        assert result["achievements"] == []
        assert result["skills"] == {}

    def test_items_missing_tags_key(self, tmp_path):
        """Items without a 'tags' key must not crash; they are silently skipped."""
        import yaml

        data = {
            "personal": {"name": "Nobody"},
            "education": [],
            "experience": [
                {
                    "company": "NoCo",
                    "role": "Engineer",
                    "dates": "2020",
                    "bullets": [
                        {"text": "No tags here"},          # missing 'tags'
                        {"text": "Also no tags"},          # missing 'tags'
                    ],
                }
            ],
            "projects": [{"name": "NoTagProject", "description": "x"}],  # missing 'tags'
            "skills": {},
            "achievements": [],
        }
        yaml_file = tmp_path / "notags.yaml"
        yaml_file.write_text(yaml.dump(data), encoding="utf-8")

        # Must not raise
        result = build_resume_data(str(yaml_file), "backend")
        # NoCo should be dropped (zero surviving bullets)
        assert result["experience"] == []

    def test_unknown_target_returns_near_empty_not_raises(self, tmp_yaml):
        """
        An unknown target that matches nothing must return empty/near-empty
        structures, not raise an exception.
        """
        result = build_resume_data(tmp_yaml, "mobile")

        # Should not raise; structure must be intact
        assert isinstance(result["experience"], list)
        assert isinstance(result["projects"], list)
        assert isinstance(result["skills"], dict)

        # Projects, achievements for 'mobile' = only general-tagged items survive
        for job in result["experience"]:
            assert len(job["bullets"]) >= 1  # at least one general bullet kept

    def test_target_stored_in_result(self, tmp_yaml):
        result = build_resume_data(tmp_yaml, "backend")
        assert result["target"] == "backend"
