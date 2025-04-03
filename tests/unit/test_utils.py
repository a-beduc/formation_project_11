from utils import load_clubs, load_competitions


def test_load_clubs():
    sut = load_clubs()
    expected_value = [
        {
            "name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": "13"
        },
        {
            "name": "Iron Temple",
            "email": "admin@irontemple.com",
            "points": "4"
        },
        {
            "name": "She Lifts",
            "email": "kate@shelifts.co.uk",
            "points": "12"
        }
    ]
    assert sut == expected_value


def test_load_competitions():
    sut = load_competitions()
    expected_value = [
        {
            "name": "Spring Festival",
            "date": "2030-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        }
    ]
    assert sut == expected_value
