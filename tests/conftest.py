import pytest
import server
from datetime import datetime, timedelta


# Set dynamic test dates: one day on the future and one in the past
now = datetime.now()
delta = timedelta(days=1)
future_d = (now + delta).strftime('%Y-%m-%d %H:%M:%S')
past_d = (now - delta).strftime('%Y-%m-%d %H:%M:%S')


@pytest.fixture
def client():
    server.app.config.update({
        "TESTING": True,
    })
    with server.app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_clubs(mocker):
    clubs = [
        {"name": "Club 001", "email": "001_club@gudlift.com", "points": 13},
        {"name": "Club 002", "email": "002_club@gudlift.com", "points": 4},
        {"name": "Club 003", "email": "003_club@gudlift.com", "points": 30},
    ]
    mocker.patch.object(server, 'clubs', clubs)
    return clubs


@pytest.fixture(autouse=True)
def mock_competitions(mocker):
    competitions = [
        {"name": "Competition 001", "date": future_d,
         "numberOfPlaces": 25},
        {"name": "Competition 002", "date": future_d,
         "numberOfPlaces": 4},
        {"name": "Competition 003", "date": past_d,
         "numberOfPlaces": 9},
        {"name": "Competition 004", "date": past_d,
         "numberOfPlaces": 3},
    ]
    past_competitions_ids = [2, 3]
    future_competitions_ids = [0, 1]

    mocker.patch.object(server, 'competitions', competitions)
    mocker.patch.object(server, 'past_competitions_ids', past_competitions_ids)
    mocker.patch.object(server, 'future_competitions_ids',
                        future_competitions_ids)
    return competitions


@pytest.fixture(autouse=True)
def mock_past_transaction(mocker):
    past_transaction = {}
    mocker.patch.object(server, 'PAST_TRANSACTION', past_transaction)
    return past_transaction
