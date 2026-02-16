"""Tests for DailyActivityService.analyze."""

from datetime import datetime, timezone

from backend.domain.models.codeforces import SubmissionStatus
from backend.domain.models.time_period import TimePeriod
from backend.domain.services.daily_activity_service import DailyActivityService


class TestAnalyzeEmptySubmissions:
    def test_empty_submissions_returns_zeros(self):
        now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = DailyActivityService.analyze("user", [], period=TimePeriod.WEEK, now=now)

        assert result.handle == "user"
        assert result.days == []
        assert result.total_solved == 0
        assert result.total_attempts == 0
        assert result.active_days == 0


class TestAnalyzeAllFailed:
    def test_all_failed_submissions(self, mock_submission):
        ts = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 1, 15, 23, 59, 0, tzinfo=timezone.utc)
        subs = [
            mock_submission(1, "A", "P1", ts, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
            mock_submission(2, "B", "P2", ts, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.WEEK, now=now)

        day_15 = next(d for d in result.days if d.date == "2025-01-15")
        assert day_15.solved_count == 0
        assert day_15.attempt_count == 2
        assert result.total_solved == 0
        assert result.total_attempts == 2


class TestAnalyzeSolvedDeduplication:
    def test_duplicate_solved_same_day_counted_once(self, mock_submission):
        ts = int(datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 1, 15, 14, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 1, 15, 23, 59, 0, tzinfo=timezone.utc)
        subs = [
            mock_submission(1, "A", "P1", ts, is_solved=True),
            mock_submission(1, "A", "P1", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.WEEK, now=now)

        day_15 = next(d for d in result.days if d.date == "2025-01-15")
        assert day_15.solved_count == 1
        assert result.total_solved == 1


class TestAnalyzeGapFilling:
    def test_missing_days_filled_with_zeros(self, mock_submission):
        ts1 = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 1, 18, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 1, 18, 23, 59, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.WEEK, now=now)

        dates = [d.date for d in result.days]
        assert "2025-01-15" in dates
        assert "2025-01-16" in dates
        assert "2025-01-17" in dates
        assert "2025-01-18" in dates

        day_16 = next(d for d in result.days if d.date == "2025-01-16")
        assert day_16.solved_count == 0
        assert day_16.attempt_count == 0
        assert result.active_days == 2


class TestAnalyzeSortOrder:
    def test_days_sorted_ascending(self, mock_submission):
        ts1 = int(datetime(2025, 1, 18, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 1, 18, 23, 59, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.WEEK, now=now)

        dates = [d.date for d in result.days]
        assert dates == sorted(dates)


class TestAnalyzeMultipleDays:
    def test_multiple_days_mixed_activity(self, mock_submission):
        ts_d1 = int(datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc).timestamp())
        ts_d2 = int(datetime(2025, 1, 16, 10, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 1, 16, 23, 59, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts_d1, is_solved=True),
            mock_submission(2, "B", "P2", ts_d1, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
            mock_submission(3, "C", "P3", ts_d2, is_solved=True),
            mock_submission(4, "D", "P4", ts_d2, is_solved=True),
            mock_submission(5, "E", "P5", ts_d2, is_solved=False, verdict=SubmissionStatus.TIME_LIMIT_EXCEEDED),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.WEEK, now=now)

        day_15 = next(d for d in result.days if d.date == "2025-01-15")
        day_16 = next(d for d in result.days if d.date == "2025-01-16")
        assert day_15.solved_count == 1
        assert day_15.attempt_count == 1
        assert day_16.solved_count == 2
        assert day_16.attempt_count == 1
        assert result.total_solved == 3
        assert result.total_attempts == 2
        assert result.active_days == 2


class TestHourlyGranularity:
    def test_day_period_produces_hourly_buckets(self, mock_submission):
        ts1 = int(datetime(2025, 1, 15, 10, 15, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 1, 15, 10, 45, 0, tzinfo=timezone.utc).timestamp())
        ts3 = int(datetime(2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 1, 15, 16, 0, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
            mock_submission(3, "C", "P3", ts3, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.DAY, now=now)

        assert any(d.date == "2025-01-15 10:00" for d in result.days)
        assert any(d.date == "2025-01-15 14:00" for d in result.days)

        hour_10 = next(d for d in result.days if d.date == "2025-01-15 10:00")
        assert hour_10.solved_count == 2
        assert hour_10.attempt_count == 0

        hour_14 = next(d for d in result.days if d.date == "2025-01-15 14:00")
        assert hour_14.solved_count == 0
        assert hour_14.attempt_count == 1


class TestMonthlyGranularity:
    def test_half_year_produces_monthly_buckets(self, mock_submission):
        ts1 = int(datetime(2025, 3, 10, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 5, 20, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=False, verdict=SubmissionStatus.WRONG_ANSWER),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.HALF_YEAR, now=now)

        dates = [d.date for d in result.days]
        assert "2024-12" in dates
        assert "2025-01" in dates
        assert "2025-03" in dates
        assert "2025-05" in dates
        assert "2025-06" in dates
        assert len(dates) == 7

        mar = next(d for d in result.days if d.date == "2025-03")
        assert mar.solved_count == 1
        assert mar.attempt_count == 0

        may = next(d for d in result.days if d.date == "2025-05")
        assert may.solved_count == 0
        assert may.attempt_count == 1

        apr = next(d for d in result.days if d.date == "2025-04")
        assert apr.solved_count == 0
        assert apr.attempt_count == 0

    def test_year_produces_monthly_buckets(self, mock_submission):
        ts1 = int(datetime(2024, 8, 5, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2025, 2, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.YEAR, now=now)

        dates = [d.date for d in result.days]
        assert dates[0] == "2024-06"
        assert dates[-1] == "2025-06"
        assert len(dates) == 13
        assert result.total_solved == 2


class TestAllTimeGranularity:
    def test_all_time_uses_year_buckets(self, mock_submission):
        ts1 = int(datetime(2022, 3, 10, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        ts2 = int(datetime(2024, 7, 20, 12, 0, 0, tzinfo=timezone.utc).timestamp())
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        subs = [
            mock_submission(1, "A", "P1", ts1, is_solved=True),
            mock_submission(2, "B", "P2", ts2, is_solved=True),
        ]

        result = DailyActivityService.analyze("user", subs, period=TimePeriod.ALL_TIME, now=now)

        dates = [d.date for d in result.days]
        assert dates == ["2022", "2023", "2024", "2025"]
        assert result.total_solved == 2
        assert result.active_days == 2
