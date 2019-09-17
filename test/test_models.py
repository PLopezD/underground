"""Data model tests."""
import datetime
import json
import os
from unittest import mock

import pytest
import pytz

from underground import SubwayFeed, models
from underground.dateutils import DEFAULT_TIMEZONE
from underground.feed import load_protobuf

from . import DATA_DIR, TEST_PROTOBUFS


def test_unix_timestamp():
    """Test that datetimes are handled correctly."""
    unix_ts = models.UnixTimestamp(time=0)
    epoch_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.timezone("UTC"))
    assert unix_ts.time == epoch_time
    assert unix_ts.timestamp_nyc == epoch_time.astimezone(
        pytz.timezone(DEFAULT_TIMEZONE)
    )


def test_extract_stop_dict():
    """Test that the correct train times are extracted.
    
    Going to use a dummy JSON file that I have edited.
    """
    with open(os.path.join(DATA_DIR, "sample_edited.json"), "r") as file:
        sample_data = json.load(file)
    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert len(stops["7"]["702N"]) == 2


@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_on_sample_protobufs(filename):
    """Make sure the model can load up one sample from all the feeds."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        data = load_protobuf(file.read())

    feed = SubwayFeed(**data)
    assert isinstance(feed, SubwayFeed)
    assert isinstance(feed.extract_stop_dict(), dict)


@mock.patch("underground.feed.request")
@pytest.mark.parametrize("filename", TEST_PROTOBUFS)
def test_get(feed_request, filename):
    """Test the get method creates the desired object."""
    with open(os.path.join(DATA_DIR, filename), "rb") as file:
        feed_request.return_value = file.read()

    feed = SubwayFeed.get(16)
    assert isinstance(feed, SubwayFeed)
    assert isinstance(feed.extract_stop_dict(), dict)


def test_trip_route_remap():
    """Test that the remapping works for a known route."""
    trip = models.Trip(
        trip_id="FAKE", start_time="01:00:00", start_date=20190101, route_id="5X"
    )
    assert trip.route_id_mapped == "5"


def test_extract_dict_route_remap():
    """Test that the route remap is active for dict extraction."""
    with open(os.path.join(DATA_DIR, "sample_edited.json"), "r") as file:
        sample_data = json.load(file)
    stops = SubwayFeed(**sample_data).extract_stop_dict()
    assert len(stops["5"]["702N"]) == 1
