import pytest
import server


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
        {"name": "Competition 001", "date": "2020-03-27 10:00:00",
         "numberOfPlaces": 25},
        {"name": "Competition 002", "date": "2020-10-22 13:30:00",
         "numberOfPlaces": 4}
    ]
    mocker.patch.object(server, 'competitions', competitions)
    return competitions


@pytest.fixture(autouse=True)
def mock_past_transaction(mocker):
    past_transaction = {}
    mocker.patch.object(server, 'PAST_TRANSACTION', past_transaction)
    return past_transaction
