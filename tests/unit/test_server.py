import pytest
import server
from html import unescape


class TestUtils:
    @pytest.mark.parametrize(
        'label, competition_index, expected_bool',
        [
            ('PAST_COMP', 3, True),
            ('FUTURE_COMP', 0, False)
        ]
    )
    def test_is_competition_in_past(
            self, mock_competitions,
            label, competition_index, expected_bool):
        sut = server.is_competition_in_past(
            mock_competitions[competition_index])
        assert sut == expected_bool

    def test_split_competitions_per_dates(self, mock_competitions):
        sut_past, sut_future = server.split_competitions_per_dates(
            mock_competitions)
        assert sut_past == [2, 3]
        assert sut_future == [0, 1]


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
        html_response = unescape(response.data.decode('utf-8'))

        assert ('<h1>Welcome to the GUDLFT Registration Portal!</h1>' in
                html_response)
        assert '<form action="showSummary" method="post">' in html_response
        assert '<input type="email" name="email" id="email"/>' in html_response
        assert ('<button type="submit" id="form-button">Enter</button>'
                in html_response)


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
        html_response = unescape(response.data.decode('utf-8'))

        assert response.status_code == expected_code
        if expected_code != 200:
            assert 'The provided email is not valid.' in html_response
        else:
            assert 'Welcome, {email}'.format(**data) in html_response


class TestBook:
    @pytest.mark.parametrize(
        'method, expected_code',
        [
            ('GET', 302),
            ('POST', 405),
            ('PUT', 405),
            ('DELETE', 405),
            ('PATCH', 405),
        ]
    )
    def test_book_route_methods(self, client, method, expected_code):
        response = client.open(path=f"/book/competition/club", method=method)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(
        'label, data, expected_code, expected_page',
        [
            ('#EMPTY', {}, 308, 'index.html'),

            ('#NO_COMPETITION', {'club': 'Club 001'},
             308, 'index.html'),

            ('#NO_CLUB', {'competition': 'Competition 001'},
             302, 'index.html'),

            ('#UNKNOWN_COMPETITION',
             {'club': 'Club 001', 'competition': 'Unknown'},
             404, 'welcome.html'),

            ('#UNKNOWN_CLUB',
             {'club': 'Unknown', 'competition': 'Competition 001'},
             302, 'index.html'),

            ('#GOOD_REQUEST',
             {'club': 'Club 001', 'competition': 'Competition 001'},
             200, 'booking.html')
        ]
    )
    def test_book_return_expected_content(
            self, client, mock_clubs, mock_competitions,
            label, data, expected_code, expected_page):
        club = data.get('club', '')
        competition = data.get('competition', '')
        response = client.get(f"/book/{competition}/{club}")
        assert response.status_code == expected_code

        if expected_code in (302, 308):
            response = client.get(f"/book/{competition}/{club}",
                                  follow_redirects=True)

        html_response = unescape(response.data.decode("utf-8"))

        if expected_page == 'index.html':
            # verify page 'title'
            assert 'GUDLFT Registration' in html_response
            assert "Lost connection, please login" in html_response
        elif expected_page == 'welcome.html':
            # verify page 'title'
            assert 'Summary | GUDLFT Registration' in html_response
            assert "Something went wrong-please try again" in html_response
        elif expected_page == 'booking.html':
            # verify page 'title'
            assert f'Booking for {competition} || GUDLFT' in html_response


class TestPurchasePlaces:
    @pytest.mark.parametrize(
        'method, expected_code',
        [
            ('GET', 405),
            ('POST', 302),
            ('PUT', 405),
            ('DELETE', 405),
            ('PATCH', 405),
        ]
    )
    def test_purchase_places_route_methods(self, client, method,
                                           expected_code):
        response = client.open(path=f"/purchasePlaces",
                               method=method)
        assert response.status_code == expected_code

    @pytest.mark.parametrize(
        "label, data, expected_code, expected_page",
        [
            ('#EMPTY', {}, 302, 'index.html'),

            ('#NO_COMPETITION', {'club': 'Club 001'},
             404, 'welcome.html'),

            ('#NO_CLUB', {'competition': 'Competition 001'},
             302, 'index.html'),

            ('#UNKNOWN_COMPETITION',
             {'club': 'Club 001', 'competition': 'Unknown'},
             404, 'welcome.html'),

            ('#UNKNOWN_CLUB',
             {'club': 'Unknown', 'competition': 'Competition 001'},
             302, 'index.html'),

            ('#GOOD_REQUEST',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 1},
             200, 'welcome.html')
        ]
    )
    def test_purchase_places_return_expected_content(
            self, client, mock_clubs, mock_competitions,
            label, data, expected_code, expected_page):
        # add assert for flashed message to anticipate for can't book past comp
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == expected_code

        if expected_code == 302:
            response = client.get(f"/book", data=data, follow_redirects=True)

        html_response = unescape(response.data.decode("utf-8"))

        if expected_page == 'index.html':
            # verify page 'title'
            assert 'GUDLFT Registration' in html_response
            assert "Lost connection, please login" in html_response
        elif expected_page == 'welcome.html' and expected_code == 404:
            # verify page 'title'
            assert 'Summary | GUDLFT Registration' in html_response
            assert "Something went wrong-please try again" in html_response
        elif expected_page == 'welcome.html' and expected_code == 200:
            # verify page 'title'
            assert 'Summary | GUDLFT Registration' in html_response
            assert "Great-booking complete!" in html_response

    @pytest.mark.parametrize(
        'label, data, expected_page, expected_code, expected_flash',
        [
            ('#BUY_OK',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 5},
             'welcome.html',
             200,
             'Great-booking complete!'),

            ('#BUY_0',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 0},
             'booking.html',
             403,
             'You must enter a valid number of places'),

            ('#BUY_WRONG_TYPE',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': "not_a_number"},
             'booking.html',
             403,
             'You must enter a valid number of places'),

            ('#BUY_NEG',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': -5},
             'booking.html',
             403,
             'You must enter a valid number of places'),

            ('#BUY_MORE_THAN_CLUB_POINTS',
             {'club': 'Club 002', 'competition': 'Competition 001',
              'places': 8},
             'booking.html',
             403,
             "You don't have enough points to proceed with your request. "
             "Requested : 8, still allowed : 4"),

            ('#BUY_MORE_THAN_COMP_PLACES',
             {'club': 'Club 001', 'competition': 'Competition 002',
              'places': 5},
             'booking.html',
             403,
             'Not enough available places for this competition. '
             'Requested : 5, still available : 4'),

            ('#BUY_MORE_THAN_12',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 13},
             'booking.html',
             403,
             "Your request exceed the maximum allowed. "
             "Requested : 13, still allowed 12")
        ]

    )
    def test_purchase_places_good_request(
            self, client, mock_clubs, mock_competitions,
            label, data, expected_page, expected_code, expected_flash):
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == expected_code

        html_response = unescape(response.data.decode("utf-8"))

        assert expected_flash in html_response

        if expected_code == 403:
            assert 'Booking for {competition} || GUDLFT'.format(
                **data) in html_response

    @pytest.mark.parametrize(
        'label, data, transaction_cache, '
        'expected_page, expected_code, expected_flash',
        [
            ("#NO_PT",
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 5},
             {},
             'welcome.html',
             200,
             'Great-booking complete!'),

            ("#NON_BLOCKING_PT",
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 5},
             {('Competition 001', 'Club 001'): 5},
             'welcome.html',
             200,
             'Great-booking complete!'),

            ("#BLOCKING_PT_NOT_MAXED",
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 5},
             {('Competition 001', 'Club 001'): 10},
             'booking.html',
             403,
             'Your request exceed the maximum allowed. Requested : 5, still '
             'allowed 2'),

            ("#BLOCKING_PT_MAXED",
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 5},
             {('Competition 001', 'Club 001'): 12},
             'welcome.html',
             302,
             'Your club has already bought 12 places for this competition. '
             'No more purchases allowed'),
        ]
    )
    def test_purchase_places_good_request_with_past_transaction(
            self, mocker, client, mock_clubs, mock_competitions,
            label, data, transaction_cache,
            expected_page, expected_code, expected_flash):

        mocker.patch.object(server, 'PAST_TRANSACTION', transaction_cache)

        transaction_key = (data['competition'], data['club'])
        cached_transaction_value = transaction_cache.get(transaction_key, 0)

        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == expected_code

        html_response = unescape(response.data.decode("utf-8"))
        assert expected_flash in html_response

        if expected_code == 200:
            assert (server.PAST_TRANSACTION[transaction_key] ==
                    cached_transaction_value + data['places'])

        if expected_code == 403:
            assert 'Booking for {competition} || GUDLFT'.format(
                **data) in html_response

    @pytest.mark.parametrize(
        'label, data, expected_page, expected_code, expected_flash',
        [
            ('#PAST_DATE',
             {'club': 'Club 001', 'competition': 'Competition 003',
              'places': 5},
             'welcome.html',
             302,
             "This competition is already over."),

            ('#FUTURE_DATE',
             {'club': 'Club 001', 'competition': 'Competition 001',
              'places': 5},
             'welcome.html',
             200,
             'Great-booking complete!'
             )
        ]
    )
    def test_purchase_places_competition_dates(
            self, client, mock_clubs, mock_competitions,
            label, data,
            expected_page, expected_code, expected_flash):
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == expected_code

        html_response = unescape(response.data.decode("utf-8"))
        assert expected_flash in html_response
        assert 'Summary | GUDLFT Registration' in html_response

    def test_purchase_places_points_updated(
            self, client, mock_clubs, mock_competitions):
        data = {'club': 'Club 001', 'competition': 'Competition 001',
                'places': 5}
        club_points_before = mock_clubs[0]['points']
        competition_places_before = mock_competitions[0]['numberOfPlaces']

        response = client.post('/purchasePlaces', data=data)
        html_response = unescape(response.data.decode("utf-8"))

        club_points_after = mock_clubs[0]['points']
        competition_places_after = mock_competitions[0]['numberOfPlaces']

        assert response.status_code == 200
        assert 'Great-booking complete!' in html_response
        assert club_points_after == club_points_before - data['places']
        assert (competition_places_after ==
                competition_places_before - data['places'])


class TestBoard:
    @pytest.mark.parametrize(
        'method, expected_code',
        [
            ('GET', 200),
            ('POST', 405),
            ('PUT', 405),
            ('DELETE', 405),
            ('PATCH', 405),
        ]
    )
    def test_board_route_methods(self, client, method, expected_code):
        response = client.open(path='/board', method=method)
        assert response.status_code == expected_code

        response_html = response.data.decode("utf-8")
        if expected_code == 200:
            assert "Club Points Board for GUDLFT" in response_html


class TestLogout:
    @pytest.mark.parametrize(
        'method, expected_code',
        [
            ('GET', 302),
            ('POST', 405),
            ('PUT', 405),
            ('DELETE', 405),
            ('PATCH', 405),
        ]
    )
    def test_logout_route_methods(self, client, method, expected_code):
        response = client.open(path='/logout', method=method)
        assert response.status_code == expected_code

    def test_logout_redirect_to_index(self, client):
        response = client.get('/logout')
        assert response.status_code == 302

        response_redirect = client.get('/logout', follow_redirects=True)
        assert response_redirect.status_code == 200

        html_redirect = response_redirect.data.decode('utf-8')
        assert 'Welcome to the GUDLFT Registration Portal!' in html_redirect
