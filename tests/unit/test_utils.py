import pytest
from datetime import datetime
from utils import (
    load_clubs,
    load_competitions,
    search_value,
    retrieve_data,
    is_competition_in_past,
    calculate_how_many_places,
    str_to_int,
    book_places,
)

LIST_OF_CLUBS = [
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

LIST_OF_COMPETITIONS = [
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


def test_load_clubs():
    sut = load_clubs()
    expected_value = LIST_OF_CLUBS
    assert sut == expected_value


def test_load_competitions():
    sut = load_competitions()
    expected_value = LIST_OF_COMPETITIONS
    assert sut == expected_value


@pytest.mark.parametrize(
    "list_of_dict, value, lookup_key, expected_result",
    [
        (LIST_OF_CLUBS, "Simply Lift", "name",
         (0, {"name": "Simply Lift",
              "email": "john@simplylift.co",
              "points": "13"})
         ),
        (LIST_OF_CLUBS, "admin@irontemple.com", "email",
         (1, {"name": "Iron Temple",
              "email": "admin@irontemple.com",
              "points": "4"})
         ),
        (LIST_OF_COMPETITIONS, "Fall Classic", "name",
         (1, {"name": "Fall Classic",
              "date": "2020-10-22 13:30:00",
              "numberOfPlaces": "13"})
         ),
    ]
)
def test_search_value(list_of_dict, value, lookup_key, expected_result):
    sut = search_value(list_of_dict, value, lookup_key)
    assert sut == expected_result


@pytest.mark.parametrize(
    "query_value, data_list, init_cache, lookup_key, expected_result",
    [
        ("john@simplylift.co",
         LIST_OF_CLUBS,
         {},
         "email",
         {"name": "Simply Lift",
          "email": "john@simplylift.co",
          "points": "13"},
         ),
        ("Iron Temple",
         LIST_OF_CLUBS,
         {},
         "name",
         {"name": "Iron Temple",
          "email": "admin@irontemple.com",
          "points": "4"},
         ),
        ("john@simplylift.co",
         LIST_OF_CLUBS,
         {"john@simplylift.co": 0},
         "email",
         {"name": "Simply Lift",
          "email": "john@simplylift.co",
          "points": "13"},
         ),
        ("unknown@email.co",
         LIST_OF_CLUBS,
         {},
         "email",
         None,
         ),
    ]
)
def test_retrieve_data(
        query_value, data_list, init_cache, lookup_key, expected_result):
    cache = init_cache.copy()
    sut = retrieve_data(
        query_value, data_list, cache, lookup_key=lookup_key)

    assert sut == expected_result

    if sut is None:
        assert query_value not in cache

    else:
        if query_value not in init_cache.keys():
            index_in_cache = cache[query_value]
            assert data_list[index_in_cache] == expected_result
        else:
            assert cache == init_cache


@pytest.mark.parametrize(
    "competition, test_date, expected_result",
    [
        (LIST_OF_COMPETITIONS[0], datetime(2029, 1, 1, 10, 0, 0), False),
        (LIST_OF_COMPETITIONS[0], datetime(2031, 1, 1, 10, 0, 0), True),
        (LIST_OF_COMPETITIONS[1], datetime(2020, 10, 21, 10, 0, 0), False),
    ]
)
def test_is_competition_in_past(competition, test_date, expected_result):
    sut = is_competition_in_past(competition, date=test_date)
    assert sut == expected_result


@pytest.mark.parametrize(
    "req_places, club_pts, comp_places, max_places, expected_result",
    [
        (0, 0, 0, 0, 0),
        (5, 12, 12, 12, 5),
        (12, 5, 12, 12, 5),
        (12, 12, 5, 12, 5),
        (12, 12, 12, 5, 5),
        (-12, 12, 12, 12, 0),
        (0, 12, 12, 12, 0),
    ]
)
def test_calculate_how_many_places(
        req_places, club_pts, comp_places, max_places, expected_result):
    sut = calculate_how_many_places(
        req_places, club_pts, comp_places, max_places)
    assert sut == expected_result


@pytest.mark.parametrize(
    "value, expected_result",
    [(1, 1),
     ("1", 1),
     (-1, -1),
     ("-1", -1),
     ("-", ValueError),
     (2.7, ValueError),
     ("2.7", ValueError),
     ("wrong_type", ValueError)])
def test_str_to_int(value, expected_result):
    if expected_result is ValueError:
        with pytest.raises(ValueError):
            str_to_int(value)
    else:
        sut = str_to_int(value)
        assert sut == expected_result


@pytest.mark.parametrize(
    "requested_places, club, competition, max_places, expected_result",
    [
        ("5", LIST_OF_CLUBS[0], LIST_OF_COMPETITIONS[0], 12,
         (str(int(LIST_OF_CLUBS[0]['points']) - 5),
          str(int(LIST_OF_COMPETITIONS[0]['numberOfPlaces']) - 5))
         ),
        ("5", LIST_OF_CLUBS[0], LIST_OF_COMPETITIONS[0], 4,
         (str(int(LIST_OF_CLUBS[0]['points']) - 4),
          str(int(LIST_OF_COMPETITIONS[0]['numberOfPlaces']) - 4))
         ),
        ("-5", LIST_OF_CLUBS[0], LIST_OF_COMPETITIONS[0], 12,
         (LIST_OF_CLUBS[0]['points'],
          LIST_OF_COMPETITIONS[0]['numberOfPlaces'])
         ),
        (4.9, LIST_OF_CLUBS[0], LIST_OF_COMPETITIONS[0], 12,
         (LIST_OF_CLUBS[0]['points'],
          LIST_OF_COMPETITIONS[0]['numberOfPlaces'])
         ),
        ("wrong_type", LIST_OF_CLUBS[0], LIST_OF_COMPETITIONS[0], 12,
         (LIST_OF_CLUBS[0]['points'],
          LIST_OF_COMPETITIONS[0]['numberOfPlaces'])
         ),
        ("-", LIST_OF_CLUBS[0], LIST_OF_COMPETITIONS[0], 12,
         (LIST_OF_CLUBS[0]['points'],
          LIST_OF_COMPETITIONS[0]['numberOfPlaces'])
         ),
    ]
)
def test_book_places(
        requested_places, club, competition, max_places, expected_result):
    sut = book_places(requested_places, club, competition, max_places)
    assert sut == expected_result
