import pytest
import server
from server import app


@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
    })
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_data(mocker):
    test_clubs = [
        {
            "name": "test_name_1",
            "email": "test_mail@test.test",
            "points": "2"
        },
        {
            "name": "test_name_2",
            "email": "test_mail2@test.test",
            "points": "16"
        }
    ]
    test_competitions = [
        {
            "name": "test_competition_past",
            "date": "2020-01-01 12:00:00",
            "numberOfPlaces": "1"
        },
        {
            "name": "test_competition_future",
            "date": "2030-12-25 18:00:00",
            "numberOfPlaces": "20"
        }
    ]
    mocker.patch.object(server, 'clubs', test_clubs)
    mocker.patch.object(server, 'competitions', test_competitions)
    return test_clubs, test_competitions


class TestIndex:
    def test_get_index(self, client, mock_data):
        response = client.get("/")
        assert response.status_code == 200


class TestShowSummary:
    def test_get_show_summary(self, client, mock_data):
        response = client.get("/showSummary")
        assert response.status_code == 302

    @pytest.mark.parametrize("data", [{'email': ''}, {}])
    def test_post_show_summary_without_email(self, client, mock_data, data):
        response = client.post("/showSummary", data=data)
        assert response.status_code == 302

    def test_post_show_summary_with_invalid_email(self, client, mock_data):
        data = {"email": "this_is_invalid_email@test.mail"}
        response = client.post("/showSummary", data=data)
        assert response.status_code == 302

    def test_post_show_summary_with_valid_email(self, client, mock_data):
        data = {'email': 'test_mail@test.test'}
        response = client.post("/showSummary", data=data)
        assert response.status_code == 200


class TestBook:
    def test_get_book_valid_club_and_valid_competition(self, client,
                                                       mock_data):
        competition = 'test_competition_future'
        club = 'test_name_1'
        response = client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200


class TestPurchasePlaces:
    def test_get_purchase_places(self, client, mock_data):
        response = client.get("/purchasePlaces")
        assert response.status_code == 405

    def test_post_purchase_places(self, client, mock_data):
        data = {'competition': 'test_competition_future',
                'club': 'test_name_1',
                'places': '1'}
        clubs, competitions = mock_data
        competition = next(
            c for c in competitions if c['name'] == data['competition']
        )
        number_of_places_before = int(competition['numberOfPlaces'])
        response = client.post("/purchasePlaces", data=data)
        number_of_places_after = int(competition['numberOfPlaces'])
        assert (number_of_places_after ==
                number_of_places_before - int(data['places']))
        assert response.status_code == 200

    def test_post_purchase_places_more_than_club_points(self, client,
                                                        mock_data):
        data = {'competition': 'test_competition_future',
                'club': 'test_name_1',
                'places': '5'}
        clubs, competitions = mock_data
        club = next(
            c for c in clubs if c['name'] == data['club']
        )
        competition = next(
            c for c in competitions if c['name'] == data['competition']
        )
        club_points = int(club['points'])
        number_of_places_before = int(competition['numberOfPlaces'])
        response = client.post("/purchasePlaces", data=data)
        number_of_places_after = int(competition['numberOfPlaces'])

        assert (number_of_places_after ==
                number_of_places_before -
                min(int(data['places']), club_points))
        assert response.status_code == 200


class TestLogout:
    def test_logout(self, client):
        response = client.get("/logout")
        assert response.status_code == 302
