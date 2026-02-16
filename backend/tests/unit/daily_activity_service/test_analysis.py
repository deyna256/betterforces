"""Tests for DailyActivityService.analyze."""

from datetime import date, datetime, timezone

from backend.domain.models.codeforces import SubmissionStatus
from backend.domain.services.daily_activity_service import DailyActivityService


class TestAnalyzeEmptySubmissions:
    def test_empty_submissions_returns_zeros(self):
        result = DailyActivityService.analyze("user", [])

        assert result.handle == "user"
        assert result.days == []
        assert result.total_solved == 0
        assert result.total_attempts == 0
        assert result.active_days == 0


class TestAnalyzeAllFailed:
    def test_all_failed_submissions(self, mock_submission):
        # 2025-01-15 00:00:00 UTC
        ts = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        subs = [
            mock_submission(1, "A", "P1", ts, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
            mock_submission(2, "B", "P2", ts, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
        ]

        result = DailyActivityService.analyze("user", subs)

        assert result.total_solved == 0
        assert result.total_attempts == 2
        assert result.active_days == 1
        assert len(result.days) == 1
        assert result.days[0].solved_count == 0
        assert result.days[0].attempt_count == 2


class TestAnalyzeSolvedDeduplication:
    def test_duplicate_solved_same_day_counted_once(self, mock_submission):
        ts = int(datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 1, 15, 14, 0, 0, tzinfo=timezone.utc).timestamp())
        # Same problem solved twice on the same day
        subs = [
            mock_submission(1, "A", "P1", ts, is_solved=True),
            mock_submission(1, "A", "P1", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs)

        assert result.total_solved == 1
        assert len(result.days) == 1
        assert result.days[0].solved_count == 1


class TestAnalyzeGapFilling:
    def test_missing_days_filled_with_zeros(self, mock_submission):
        # Day 1: Jan 15
        ts1 = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        # Day 2: Jan 18 (3-day gap)
        ts2 = int(datetime(2025, 1, 18, 12, 0, 0, tzinfo=timezone.utc).timestamp())

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs)

        assert len(result.days) == 4  # Jan 15, 16, 17, 18
        assert result.days[0].date == "2025-01-15"
        assert result.days[0].solved_count == 1
        assert result.days[1].date == "2025-01-16"
        assert result.days[1].solved_count == 0
        assert result.days[1].attempt_count == 0
        assert result.days[2].date == "2025-01-17"
        assert result.days[2].solved_count == 0
        assert result.days[3].date == "2025-01-18"
        assert result.days[3].solved_count == 1
        assert result.active_days == 2


class TestAnalyzeSortOrder:
    def test_days_sorted_ascending(self, mock_submission):
        ts1 = int(datetime(2025, 1, 18, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs)

        dates = [d.date for d in result.days]
        assert dates == sorted(dates)
        assert dates[0] == "2025-01-15"
        assert dates[-1] == "2025-01-18"


class TestAnalyzeMultipleDays:
    def test_multiple_days_mixed_activity(self, mock_submission):
        ts_d1 = int(datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc).timestamp())
        ts_d2 = int(datetime(2025, 1, 16, 10, 0, 0, tzinfo=timezone.utc).timestamp())

        subs = [
            mock_submission(1, "A", "P1", ts_d1, is_solved=True),
            mock_submission(2, "B", "P2", ts_d1, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
            mock_submission(3, "C", "P3", ts_d2, is_solved=True),
            mock_submission(4, "D", "P4", ts_d2, is_solved=True),
            mock_submission(5, "E", "P5", ts_d2, is_solved=False, verdict=SubmissionStatus.TIME_LIMIT_EXCEEDED),
        ]

        result = DailyActivityService.analyze("user", subs)

        assert len(result.days) == 2
        assert result.days[0].date == "2025-01-15"
        assert result.days[0].solved_count == 1
        assert result.days[0].attempt_count == 1
        assert result.days[1].date == "2025-01-16"
        assert result.days[1].solved_count == 2
        assert result.days[1].attempt_count == 1
        assert result.total_solved == 3
        assert result.total_attempts == 2
        assert result.active_days == 2


class TestAnalyzeWithDateBoundaries:
    def test_start_and_end_date_expand_range(self, mock_submission):
        ts = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        subs = [mock_submission(1, "A", "P1", ts, is_solved=True)]

        result = DailyActivityService.analyze(
            "user",
            subs,
            start_date=date(2025, 1, 13),
            end_date=date(2025, 1, 17),
        )

        assert len(result.days) == 5  # Jan 13-17
        assert result.days[0].date == "2025-01-13"
        assert result.days[0].solved_count == 0
        assert result.days[2].date == "2025-01-15"
        assert result.days[2].solved_count == 1
        assert result.days[4].date == "2025-01-17"
        assert result.days[4].solved_count == 0
