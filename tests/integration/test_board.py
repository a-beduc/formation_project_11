"""
Integration tests for the main Flask application defined in server.py

This module tests the board functionalities

Fixtures such as 'client', 'mock_clubs', 'mock_competitions' are defined
in a 'conftest.py' file and injected by pytest during test.
"""


def test_board_points_updated_after_purchase(
        client, mock_clubs, mock_competitions):
    # Verify club points before any transaction
    response_board = client.get("/board")
    html_response_board = response_board.data.decode("utf-8")
    html_response_board_no_space = (
        html_response_board.replace(" ", "").replace("\n", ""))

    assert response_board.status_code == 200
    assert 'Club Points Board for GUDLFT' in html_response_board
    assert '<td>Club001</td><td>13</td>' in html_response_board_no_space
    assert '<td>Club002</td><td>4</td>' in html_response_board_no_space
    assert '<td>Club003</td><td>30</td>' in html_response_board_no_space

    # Club 001 buy 5 from Competition 001
    # Club 003 Buy 10 from Competition 001
    request_args_club_001 = {'club': 'Club 001',
                             'competition': 'Competition 001',
                             'places': '5'}
    client.post('/purchasePlaces', data=request_args_club_001)

    request_args_club_003 = {'club': 'Club 003',
                             'competition': 'Competition 001',
                             'places': '10'}
    client.post('/purchasePlaces', data=request_args_club_003)

    # Verify club points after any transaction
    response_board = client.get("/board")
    html_response_board = response_board.data.decode("utf-8")
    html_response_board_no_space = (html_response_board.replace(" ", "").
                                    replace("\n", ""))
    assert response_board.status_code == 200
    assert 'Club Points Board for GUDLFT' in html_response_board
    assert '<td>Club001</td><td>8</td>' in html_response_board_no_space
    assert '<td>Club002</td><td>4</td>' in html_response_board_no_space
    assert '<td>Club003</td><td>20</td>' in html_response_board_no_space
