"""Tests for BaseMetricController._filter_by_date_range()."""

from datetime import datetime, timezone
from unittest.mock import Mock

from backend.api.routes.base import BaseMetricController
from backend.domain.models import Submission


def _make_submission(timestamp: int) -> Mock:
    """Create a mock submission with the given creation_time_seconds."""
    sub = Mock(spec=Submission)
    sub.creation_time_seconds = timestamp
    return sub


class TestFilterByDateRange:
    """Tests for _filter_by_date_range static method."""

    def test_no_filters_returns_all(self):
        subs = [_make_submission(100), _make_submission(200), _make_submission(300)]
        result = BaseMetricController._filter_by_date_range(subs)
        assert len(result) == 3

    def test_start_date_only(self):
        subs = [_make_submission(100), _make_submission(200), _make_submission(300)]
        start = datetime(1970, 1, 1, 0, 3, 15, tzinfo=timezone.utc)  # timestamp 195
        result = BaseMetricController._filter_by_date_range(subs, start_date=start)
        assert len(result) == 2
        assert all(s.creation_time_seconds >= 195 for s in result)

    def test_end_date_only(self):
        subs = [_make_submission(100), _make_submission(200), _make_submission(300)]
        end = datetime(1970, 1, 1, 0, 3, 15, tzinfo=timezone.utc)  # timestamp 195
        result = BaseMetricController._filter_by_date_range(subs, end_date=end)
        assert len(result) == 1
        assert result[0].creation_time_seconds == 100

    def test_both_start_and_end(self):
        subs = [_make_submission(100), _make_submission(200), _make_submission(300)]
        start = datetime(1970, 1, 1, 0, 2, 30, tzinfo=timezone.utc)  # timestamp 150
        end = datetime(1970, 1, 1, 0, 4, 10, tzinfo=timezone.utc)  # timestamp 250
        result = BaseMetricController._filter_by_date_range(subs, start_date=start, end_date=end)
        assert len(result) == 1
        assert result[0].creation_time_seconds == 200

    def test_none_parameters_no_filtering(self):
        subs = [_make_submission(100), _make_submission(200)]
        result = BaseMetricController._filter_by_date_range(subs, start_date=None, end_date=None)
        assert len(result) == 2

    def test_empty_submissions_list(self):
        result = BaseMetricController._filter_by_date_range([])
        assert result == []

    def test_empty_submissions_with_dates(self):
        start = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        result = BaseMetricController._filter_by_date_range([], start_date=start, end_date=end)
        assert result == []

    def test_inclusive_boundaries(self):
        # start_date and end_date should be inclusive (>= and <=)
        subs = [_make_submission(100), _make_submission(200), _make_submission(300)]
        start = datetime(1970, 1, 1, 0, 1, 40, tzinfo=timezone.utc)  # timestamp 100
        end = datetime(1970, 1, 1, 0, 5, 0, tzinfo=timezone.utc)  # timestamp 300
        result = BaseMetricController._filter_by_date_range(subs, start_date=start, end_date=end)
        assert len(result) == 3
