"""Tests for TimePeriod.to_start_date()."""

from datetime import datetime, timezone

from backend.domain.models.time_period import TimePeriod


class TestToStartDate:
    """Tests for TimePeriod.to_start_date method."""

    def test_all_time_returns_none(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        assert TimePeriod.ALL_TIME.to_start_date(now) is None

    def test_hour(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.HOUR.to_start_date(now)
        assert result == datetime(2025, 6, 15, 11, 0, 0, tzinfo=timezone.utc)

    def test_day(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.DAY.to_start_date(now)
        assert result == datetime(2025, 6, 14, 12, 0, 0, tzinfo=timezone.utc)

    def test_week(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.WEEK.to_start_date(now)
        assert result == datetime(2025, 6, 8, 12, 0, 0, tzinfo=timezone.utc)

    def test_month(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.MONTH.to_start_date(now)
        assert result == datetime(2025, 5, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_month_january_wraps_to_december(self):
        now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.MONTH.to_start_date(now)
        assert result == datetime(2024, 12, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_month_end_of_month_clamping(self):
        # March 31 -> February has only 28 days
        now = datetime(2025, 3, 31, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.MONTH.to_start_date(now)
        assert result == datetime(2025, 2, 28, 12, 0, 0, tzinfo=timezone.utc)

    def test_month_end_of_month_leap_year(self):
        # March 31 in a leap year -> February 29
        now = datetime(2024, 3, 31, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.MONTH.to_start_date(now)
        assert result == datetime(2024, 2, 29, 12, 0, 0, tzinfo=timezone.utc)

    def test_half_year(self):
        now = datetime(2025, 8, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.HALF_YEAR.to_start_date(now)
        assert result == datetime(2025, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_half_year_wraps_to_previous_year(self):
        now = datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.HALF_YEAR.to_start_date(now)
        assert result == datetime(2024, 9, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_half_year_end_of_month_clamping(self):
        # Aug 31 -> Feb has only 28 days
        now = datetime(2025, 8, 31, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.HALF_YEAR.to_start_date(now)
        assert result == datetime(2025, 2, 28, 12, 0, 0, tzinfo=timezone.utc)

    def test_year(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.YEAR.to_start_date(now)
        assert result == datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_year_leap_day(self):
        # Feb 29 in leap year -> Feb 28 in non-leap year
        now = datetime(2024, 2, 29, 12, 0, 0, tzinfo=timezone.utc)
        result = TimePeriod.YEAR.to_start_date(now)
        assert result == datetime(2023, 2, 28, 12, 0, 0, tzinfo=timezone.utc)

    def test_preserves_timezone(self):
        now = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        for period in TimePeriod:
            result = period.to_start_date(now)
            if result is not None:
                assert result.tzinfo == timezone.utc
