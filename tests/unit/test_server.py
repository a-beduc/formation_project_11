import pytest
import server


@pytest.fixture
def client():
    server.app.config.update({
        "TESTING": True,
    })
    with server.app.test_client() as client:
        yield client


@pytest.fixture
def mock_clubs(mocker):
    clubs = [
        {"name": "Club 001", "email": "001_club@gudlift.com", "points": "13"},
        {"name": "Club 002", "email": "002_club@gudlift.com", "points": "4"},
        {"name": "Club 003", "email": "003_club@gudlift.com", "points": "30"},
    ]
    mocker.patch.object(server, 'clubs', clubs)
    return clubs


@pytest.fixture
def mock_competitions(mocker):
    competitions = [
        {"name": "Competition 001", "date": "2020-03-27 10:00:00",
         "numberOfPlaces": "25"},
        {"name": "Competition 002", "date": "2020-10-22 13:30:00",
         "numberOfPlaces": "13"}
    ]
    mocker.patch.object(server, 'competitions', competitions)
    return competitions


class TestIndex:
    @pytest.mark.parametrize(
        'method, expected_code',
        [
            ('GET', 200),
            ('POST', 405),
            ('PUT', 405),
            ('DELETE', 405),
            ('PATCH', 405),
        ])
    def test_index_route_methods(self, client, method, expected_code):
        response = client.open(path='/', method=method)
        assert response.status_code == expected_code

    def test_index_contains_expected_elements(self, client):
        response = client.get('/')
        html = response.data.decode('utf-8')

        assert '<h1>Welcome to the GUDLFT Registration Portal!</h1>' in html
        assert '<form action="showSummary" method="post">' in html
        assert '<input type="email" name="email" id=""/>' in html
        assert '<button type="submit">Enter</button>' in html


class TestShowSummary:
    @pytest.mark.parametrize(
        'method, expected_code',
        [
            ('GET', 405),
            ('POST', 401),
            ('PUT', 405),
            ('DELETE', 405),
            ('PATCH', 405),
        ]
    )
    def test_show_summary_route_methods(self, client, method, expected_code):
        response = client.open(path='/showSummary', method=method)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(
        'label, data, expected_code',
        [
            ('#NO_EMAIL', {}, 401),
            ('#EMPTY_EMAIL', {'email': ""}, 401),
            ('#WRONG_EMAIL', {'email': 'unknown@email'}, 401),
            ('#RIGHT_EMAIL', {'email': '001_club@gudlift.com'}, 200)
        ]
    )
    def test_login_email(self, client, mock_clubs, mock_competitions,
                         label, data, expected_code):
        response = client.post(path='/showSummary', data=data)
        html = response.data.decode('utf-8')

        if expected_code != 200:
            assert 'The provided email is not valid.' in html

        assert response.status_code == expected_code
