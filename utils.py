import json
from datetime import datetime


def load_clubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


def search_value(list_of_dict, value, lookup_key="name"):
    return next(((i, elem) for i, elem in enumerate(list_of_dict)
                 if elem[lookup_key] == value), (None, None))


def retrieve_data(query_value, data_list, cache_dict, lookup_key='name'):
    cached_index = cache_dict.get(query_value)
    if cached_index is not None:
        return data_list[cached_index]

    index, obj = search_value(data_list, query_value, lookup_key=lookup_key)
    if index is not None:
        cache_dict[query_value] = index
    return obj


def is_competition_in_past(competition, date=None):
    time_directive = '%Y-%m-%d %H:%M:%S'
    time_competition = competition.get('date', None)
    date = date or datetime.today()
    return date > datetime.strptime(time_competition, time_directive)


def calculate_how_many_places(req_places, club_pts, comp_places, max_places):
    return min(max_places, max(0, req_places), club_pts, comp_places)


def str_to_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.isdigit() or (
                len(value) > 1 and
                value.startswith('-') and
                value[1:].isdigit()):
            return int(value)
    raise ValueError


def book_places(requested_places, club, competition, max_places):
    comp_places = int(competition['numberOfPlaces'])
    club_pts = int(club['points'])
    try:
        req_places = str_to_int(requested_places) if requested_places else 0
    except ValueError:
        req_places = 0
    max_places = int(max_places)

    places_to_book = calculate_how_many_places(
        req_places, club_pts, comp_places, max_places)
    if places_to_book:
        comp_places -= places_to_book
        club_pts -= places_to_book
    return str(club_pts), str(comp_places)
