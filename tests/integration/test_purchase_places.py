"""
Integration tests for the main Flask application defined in server.py

This module tests the purchase functionalities

Fixtures such as 'client', 'mock_clubs', 'mock_competitions' are defined
in a 'conftest.py' file and injected by pytest during test.
"""


from html import unescape


def test_purchase_places_flow_success(client, mock_clubs, mock_competitions):
    # Login as Club 001
    response_login = client.post("/showSummary",
                                 data={"email": "001_club@gudlift.com"})
    html_response_login = response_login.data.decode("utf-8")
    assert response_login.status_code == 200
    assert 'Welcome, 001_club@gudlift.com' in html_response_login
    assert 'Competition 001' in html_response_login

    # Verify score in memory and on template
    assert mock_competitions[0]['numberOfPlaces'] == 25
    assert mock_clubs[0]['points'] == 13
    assert 'Number of Places: 25' in html_response_login

    # Get Competition 001 with Club 001
    book_url = "/book/Competition 001/Club 001"
    response_book = client.get(book_url)
    html_response_book = response_book.data.decode("utf-8")
    assert response_book.status_code == 200
    assert (f"Booking for {mock_competitions[0]['name']} || GUDLFT"
            in html_response_book)

    # Post a purchase of 5 places from Club 001 to Competition 001
    request_args = {'club': 'Club 001',
                    'competition': 'Competition 001',
                    'places': '5'}
    response_purchase_places = client.post('/purchasePlaces',
                                           data=request_args)
    html_response_purchase_places = (
        response_purchase_places.data.decode("utf-8"))
    assert response_purchase_places.status_code == 200
    assert 'Great-booking complete!' in html_response_purchase_places

    # Verify updated score in memory and on template
    assert mock_competitions[0]['numberOfPlaces'] == 20
    assert mock_clubs[0]['points'] == 8
    assert 'Number of Places: 20' in html_response_purchase_places


def test_purchase_places_more_than_club_points(
        client, mock_clubs, mock_competitions):
    # Login as Club 002
    response_login = client.post("/showSummary",
                                 data={"email": "002_club@gudlift.com"})
    html_response_login = response_login.data.decode("utf-8")
    assert response_login.status_code == 200
    assert 'Welcome, 002_club@gudlift.com' in html_response_login
    assert 'Competition 001' in html_response_login

    # Verify score in memory and on template
    assert mock_competitions[0]['numberOfPlaces'] == 25
    assert mock_clubs[1]['points'] == 4
    assert 'Number of Places: 25' in html_response_login

    # Get Competition 001 with Club 002
    book_url = "/book/Competition 001/Club 002"
    response_book = client.get(book_url)
    html_response_book = response_book.data.decode("utf-8")
    assert response_book.status_code == 200
    assert (f"Booking for {mock_competitions[0]['name']} || GUDLFT"
            in html_response_book)

    # Post a purchase of 5 places from Club 002 to Competition 001
    request_args = {'club': 'Club 002',
                    'competition': 'Competition 001',
                    'places': '5'}
    response_purchase_places = client.post('/purchasePlaces',
                                           data=request_args)
    html_response_purchase_places = unescape(
        response_purchase_places.data.decode("utf-8"))
    assert response_purchase_places.status_code == 400
    assert (("You don't have enough points to proceed with your request. "
            "Requested : 5, still allowed : 4")
            in html_response_purchase_places)

    # Verify not updated score in memory and on template
    assert mock_competitions[0]['numberOfPlaces'] == 25
    assert mock_clubs[1]['points'] == 4
    assert 'Places available: 25' in html_response_purchase_places


def test_purchase_places_more_than_competition_places(
        client, mock_clubs, mock_competitions):
    # Login as Club 001
    response_login = client.post("/showSummary",
                                 data={"email": "001_club@gudlift.com"})
    html_response_login = response_login.data.decode("utf-8")
    assert response_login.status_code == 200
    assert 'Welcome, 001_club@gudlift.com' in html_response_login
    assert 'Competition 002' in html_response_login

    # Verify score in memory and on template
    assert mock_competitions[1]['numberOfPlaces'] == 4
    assert mock_clubs[0]['points'] == 13
    assert 'Number of Places: 4' in html_response_login

    # Get Competition 002 with Club 001
    book_url = "/book/Competition 002/Club 001"
    response_book = client.get(book_url)
    html_response_book = response_book.data.decode("utf-8")
    assert response_book.status_code == 200
    assert (f"Booking for {mock_competitions[1]['name']} || GUDLFT" in
            html_response_book)

    # Post a purchase of 5 places from Club 001 to Competition 002
    request_args = {'club': 'Club 001',
                    'competition': 'Competition 002',
                    'places': '5'}
    response_purchase_places = client.post(
        '/purchasePlaces', data=request_args)
    html_response_purchase_places = unescape(
        response_purchase_places.data.decode("utf-8"))
    assert response_purchase_places.status_code == 400
    assert (('Not enough available places for this competition. '
            'Requested : 5, still available : 4')
            in html_response_purchase_places)

    # Verify not updated score in memory and on template
    assert mock_competitions[1]['numberOfPlaces'] == 4
    assert mock_clubs[0]['points'] == 13
    assert 'Places available: 4' in html_response_purchase_places


def test_purchase_7_places_twice_to_try_to_bypass_maximum(
        client, mock_clubs, mock_competitions, mock_past_transaction):
    # Verify score in memory
    assert mock_competitions[0]['numberOfPlaces'] == 25
    assert mock_clubs[2]['points'] == 30
    assert mock_past_transaction == {}

    # Get Competition 001 with Club 003
    book_url = "/book/Competition 001/Club 003"
    response_book = client.get(book_url)
    html_response_book = response_book.data.decode("utf-8")
    assert response_book.status_code == 200
    assert (f"Booking for {mock_competitions[0]['name']} || GUDLFT"
            in html_response_book)

    # Post a purchase of 7 places from Club 003 to Competition 001
    request_args = {'club': 'Club 003',
                    'competition': 'Competition 001',
                    'places': '7'}
    response_purchase_places = client.post('/purchasePlaces',
                                           data=request_args)
    html_response_purchase_places = (
        response_purchase_places.data.decode("utf-8"))

    assert response_purchase_places.status_code == 200
    assert 'Great-booking complete!' in html_response_purchase_places

    # Verify score in memory, score in template, cached past transaction
    assert mock_competitions[0]['numberOfPlaces'] == 18
    assert mock_clubs[2]['points'] == 23
    assert 'Number of Places: 18' in html_response_purchase_places
    assert mock_past_transaction[('Competition 001', 'Club 003')] == 7

    # Post a purchase of 7 places from Club 003 to Competition 001
    second_request_args = {'club': 'Club 003',
                           'competition': 'Competition 001',
                           'places': '7'}
    second_response_purchase_places = client.post('/purchasePlaces',
                                                  data=second_request_args)
    second_html_response_purchase_places = (
        second_response_purchase_places.data.decode("utf-8"))
    assert second_response_purchase_places.status_code == 400
    assert (f"Booking for {mock_competitions[0]['name']} || GUDLFT"
            in second_html_response_purchase_places)
    assert ('Your request exceed the maximum allowed. Requested : 7, still '
            'allowed 5') in second_html_response_purchase_places

    # Verify not updated score in memory
    assert mock_competitions[0]['numberOfPlaces'] == 18
    assert mock_clubs[2]['points'] == 23


def test_purchase_7_places_then_5_to_reach_maximum(
        client, mock_clubs, mock_competitions, mock_past_transaction):
    # Verify score in memory
    assert mock_competitions[0]['numberOfPlaces'] == 25
    assert mock_clubs[2]['points'] == 30
    assert mock_past_transaction == {}

    # Get Competition 001 with Club 003
    book_url = "/book/Competition 001/Club 003"
    response_book = client.get(book_url)
    html_response_book = response_book.data.decode("utf-8")
    assert response_book.status_code == 200
    assert (f"Booking for {mock_competitions[0]['name']} || GUDLFT"
            in html_response_book)

    # Post a purchase of 7 places from Club 003 to Competition 001
    request_args = {'club': 'Club 003',
                    'competition': 'Competition 001',
                    'places': '7'}
    response_purchase_places = client.post('/purchasePlaces',
                                           data=request_args)
    html_response_purchase_places = (
        response_purchase_places.data.decode("utf-8"))
    assert response_purchase_places.status_code == 200
    assert 'Great-booking complete!' in html_response_purchase_places

    # Verify score in memory, score in template, cached past transaction
    assert 'Number of Places: 18' in html_response_purchase_places
    assert mock_competitions[0]['numberOfPlaces'] == 18
    assert mock_clubs[2]['points'] == 23
    assert mock_past_transaction[('Competition 001', 'Club 003')] == 7

    # Post a purchase of 5 places from Club 003 to Competition 001
    second_request_args = {'club': 'Club 003',
                           'competition': 'Competition 001',
                           'places': '5'}
    second_response_purchase_places = client.post('/purchasePlaces',
                                                  data=second_request_args)
    second_html_response_purchase_places = (
        second_response_purchase_places.data.decode("utf-8"))
    assert second_response_purchase_places.status_code == 200
    assert 'Great-booking complete!' in second_html_response_purchase_places

    # Verify score in memory, cached past transaction
    assert mock_past_transaction[('Competition 001', 'Club 003')] == 12
    assert mock_competitions[0]['numberOfPlaces'] == 13
    assert mock_clubs[2]['points'] == 18


def test_try_to_purchase_past_competition(
        client, mock_clubs, mock_competitions):
    # Verify score in memory
    assert mock_competitions[3]['numberOfPlaces'] == 3
    assert mock_clubs[0]['points'] == 13

    # Get Competition 001 with Club 004
    book_url = "/book/Competition 004/Club 001"
    response_book = client.get(book_url)
    html_response_book = response_book.data.decode("utf-8")
    assert response_book.status_code == 200
    assert (f"Booking for {mock_competitions[3]['name']} || GUDLFT"
            in html_response_book)

    # Post a purchase of 1 place from Club 001 to Competition 004
    request_args = {'club': 'Club 001',
                    'competition': 'Competition 004',
                    'places': '1'}
    response_purchase_places = client.post('/purchasePlaces',
                                           data=request_args)
    html_response_purchase_places = (
        response_purchase_places.data.decode("utf-8"))
    assert response_purchase_places.status_code == 302
    assert 'This competition is already over.' in html_response_purchase_places

    # Verify score in memory and on template
    assert mock_competitions[3]['numberOfPlaces'] == 3
    assert mock_clubs[0]['points'] == 13
    assert 'Number of Places: 3' in html_response_purchase_places
