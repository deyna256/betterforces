"""Tests for division extraction from contest names."""

from backend.infrastructure.codeforces_client import CodeforcesClient


def test_extracts_div_1() -> None:
    assert CodeforcesClient._extract_division("Codeforces Round 123 (Div. 1)") == "Div. 1"


def test_extracts_div_2() -> None:
    assert CodeforcesClient._extract_division("Codeforces Round 456 (Div. 2)") == "Div. 2"


def test_extracts_div_3() -> None:
    assert CodeforcesClient._extract_division("Codeforces Round 789 (Div. 3)") == "Div. 3"


def test_extracts_div_4() -> None:
    assert CodeforcesClient._extract_division("Codeforces Round 999 (Div. 4)") == "Div. 4"


def test_extracts_combined_div_1_and_2() -> None:
    # For combined rounds, should return the harder division (lower number)
    assert CodeforcesClient._extract_division("Codeforces Round 100 (Div. 1 + Div. 2)") == "Div. 1"


def test_extracts_combined_div_2_and_1() -> None:
    # Order shouldn't matter
    assert CodeforcesClient._extract_division("Codeforces Round 100 (Div. 2 + Div. 1)") == "Div. 1"


def test_returns_none_for_educational_round() -> None:
    assert CodeforcesClient._extract_division("Educational Codeforces Round 123") is None


def test_returns_none_for_global_round() -> None:
    assert CodeforcesClient._extract_division("Codeforces Global Round 20") is None


def test_extracts_with_different_spacing() -> None:
    assert CodeforcesClient._extract_division("Codeforces Round 123 (Div.2)") == "Div. 2"
    assert CodeforcesClient._extract_division("Codeforces Round 123 (Div. 2 )") == "Div. 2"


def test_case_insensitive_extraction() -> None:
    assert CodeforcesClient._extract_division("Contest (div. 2)") == "Div. 2"
    assert CodeforcesClient._extract_division("Contest (DIV. 2)") == "Div. 2"


def test_returns_none_for_empty_string() -> None:
    assert CodeforcesClient._extract_division("") is None


def test_extracts_from_complex_contest_name() -> None:
    name = "Codeforces Round #855 (Div. 1, based on VK Cup 2023 - Elimination)"
    assert CodeforcesClient._extract_division(name) == "Div. 1"


def test_extracts_from_contest_with_multiple_parts() -> None:
    name = "Codeforces Round #100500 (Div. 3, sponsored by Some Company)"
    assert CodeforcesClient._extract_division(name) == "Div. 3"
