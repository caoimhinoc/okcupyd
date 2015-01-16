import datetime

import unittest.mock
import pytest

from okcupyd import helpers


@pytest.yield_fixture(autouse=True, scope='module')
def mock_datetime():
    class PatchedDatetime(datetime.datetime):
        now_ = None
        @classmethod
        def today(cls):
            return cls.now().date()

        @classmethod
        def now(cls):
            return cls.now_
    PatchedDatetime.now_ = PatchedDatetime(year=2014, month=2, day=3,
                                           hour=12, minute=3)
    with mock.patch('okcupyd.helpers.datetime', PatchedDatetime):
        yield PatchedDatetime


def test_parse_date_updated_day_of_the_week():
    assert (helpers.parse_date_updated('Tuesday') -
            helpers.parse_date_updated('Monday') == datetime.timedelta(days=1))


def test_parse_day_of_the_week_has_zero_hours_seconds_and_minutes():
    parsed = helpers.parse_date_updated('Sunday')
    assert parsed.hour == 0
    assert parsed.minute == 0
    assert parsed.second == 0


def test_parse_date_updated_handles_slash_dates():
    assert helpers.parse_date_updated('11/22/99') == datetime.datetime(
        year=1999, day=22, month=11
    )


def test_parse_date_updated_handles_times(mock_datetime):
    assert helpers.parse_date_updated('10:11pm') == mock_datetime.now_.replace(
        hour=22, minute=11, day=mock_datetime.now_.day - 1
    )
    assert helpers.parse_date_updated('11:59am') == mock_datetime.now_.replace(
        hour=11, minute=59
    )
    assert helpers.parse_date_updated('12:00am') == mock_datetime.now_.replace(
        hour=0, minute=0
    )


def test_parse_date_handles_month_abbreviation_day_pairs():
    assert helpers.parse_date_updated('Jan 12') == datetime.datetime(
        year=2014, month=1, day=12
    )
    assert helpers.parse_date_updated('Jan 31') == datetime.datetime(
        year=2014, month=1,day=31
    )
    assert helpers.parse_date_updated('Feb 28') == datetime.datetime(
        year=2014, month=2, day=28
    )


def test_parse_time_on_last_day_of_month(mock_datetime):
    mock_datetime.now_ = mock_datetime(year=2014, month=10, day=1)
    assert helpers.parse_date_updated('11:00pm').month == 9


def test_parse_time_on_contextual_descriptions(mock_datetime):
    assert helpers.parse_date_updated('Just Now!') == mock_datetime.now_
    assert helpers.parse_date_updated('Yesterday') == \
        mock_datetime.now_ - datetime.timedelta(days=1)
