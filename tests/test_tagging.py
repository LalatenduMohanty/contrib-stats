"""Tests for keyword-based comment classification."""

import pytest

from contrib_stats.tagging import KeywordTagger


@pytest.fixture
def tagger():
    return KeywordTagger()


class TestClassify:
    def test_empty_body(self, tagger):
        assert tagger.classify("") == set()
        assert tagger.classify(None) == set()

    def test_no_match(self, tagger):
        assert tagger.classify("looks good to me, ship it") == set()

    def test_bug_keywords(self, tagger):
        assert "bug" in tagger.classify("this looks like a bug in the parser")
        assert "bug" in tagger.classify("need to fix this edge case")
        assert "bug" in tagger.classify("this will crash on empty input")
        assert "bug" in tagger.classify("ERROR: null pointer")
        assert "bug" in tagger.classify("this will fail if x is None")
        assert "bug" in tagger.classify("regression from last release")

    def test_security_keywords(self, tagger):
        assert "security" in tagger.classify("security concern here")
        assert "security" in tagger.classify("potential SQL injection")
        assert "security" in tagger.classify("CVE-2024-1234 applies here")
        assert "security" in tagger.classify("check auth before proceeding")
        assert "security" in tagger.classify("credential leak risk")

    def test_test_keywords(self, tagger):
        assert "test" in tagger.classify("need a test for this path")
        assert "test" in tagger.classify("coverage is low here")
        assert "test" in tagger.classify("add an assert for the return value")
        assert "test" in tagger.classify("mock the database connection")

    def test_design_keywords(self, tagger):
        assert "design" in tagger.classify("we should refactor this")
        assert "design" in tagger.classify("naming is confusing here")
        assert "design" in tagger.classify("high complexity in this function")
        assert "design" in tagger.classify("tight coupling between modules")
        assert "design" in tagger.classify("readability could be improved")

    def test_multiple_categories(self, tagger):
        result = tagger.classify("this bug needs a test and a refactor")
        assert result == {"bug", "test", "design"}

    def test_case_insensitive(self, tagger):
        assert "bug" in tagger.classify("BUG in the handler")
        assert "security" in tagger.classify("SECURITY vulnerability")

    def test_word_boundary(self, tagger):
        assert "test" not in tagger.classify("the latest version works")
        assert "bug" not in tagger.classify("debugging is fun")


class TestSignals:
    def test_quality_signal(self, tagger):
        assert tagger.has_quality_signal({"design"})
        assert tagger.has_quality_signal({"design", "bug"})
        assert not tagger.has_quality_signal({"bug"})
        assert not tagger.has_quality_signal(set())

    def test_issue_signal(self, tagger):
        assert tagger.has_issue_signal({"bug"})
        assert tagger.has_issue_signal({"security"})
        assert tagger.has_issue_signal({"test"})
        assert tagger.has_issue_signal({"bug", "test"})
        assert not tagger.has_issue_signal({"design"})
        assert not tagger.has_issue_signal(set())


class TestCustomCategories:
    def test_custom_keywords(self):
        tagger = KeywordTagger(categories={"perf": ["slow", "latency", "bottleneck"]})
        assert tagger.classify("this is slow") == {"perf"}
        assert tagger.classify("a bug here") == set()
