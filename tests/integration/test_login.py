"""
Integration tests for the main Flask application defined in server.py

This module tests the login and logout functionalities

Fixtures such as 'client', 'mock_clubs', 'mock_competitions' are defined
in a 'conftest.py' file and injected by pytest during test.
"""


def test_login_flow_success(client, mock_clubs, mock_competitions):
    # Get login page
    response_index = client.get("/")
    assert response_index.status_code == 200

    # Login as Club 001
    response_login = client.post("/showSummary",
                                 data={"email": "001_club@gudlift.com"})
    html_response = response_login.data.decode("utf-8")
    assert response_login.status_code == 200
    assert 'Welcome, 001_club@gudlift.com' in html_response
    assert 'Competition 001' in html_response


def test_login_flow_failure(client, mock_clubs, mock_competitions):
    # Get login page
    response_index = client.get("/")
    assert response_index.status_code == 200

    # Try to log in with an unknown email
    response_login = client.post("/showSummary",
                                 data={"email": "unknown@gudlift.com"})
    html_response = response_login.data.decode("utf-8")
    assert response_login.status_code == 401
    assert 'Welcome to the GUDLFT Registration Portal!' in html_response


def test_logout_flow_success(client, mock_clubs, mock_competitions):
    # Login as Club 001
    response_login = client.post("/showSummary",
                                 data={"email": "001_club@gudlift.com"})
    html_login = response_login.data.decode("utf-8")
    assert response_login.status_code == 200
    assert 'Welcome, 001_club@gudlift.com' in html_login
    assert 'Competition 001' in html_login

    # Log out and track redirect to index
    response_logout = client.get("/logout", follow_redirects=True)
    html_logout = response_logout.data.decode("utf-8")
    assert response_logout.status_code == 200
    assert 'Welcome to the GUDLFT Registration Portal!' in html_logout
