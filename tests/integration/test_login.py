def test_login_flow_success(client, mock_clubs, mock_competitions):
    response_index = client.get("/")
    assert response_index.status_code == 200

    response_login = client.post("/showSummary",
                                 data={"email": "001_club@gudlift.com"})
    assert response_login.status_code == 200

    html_response = response_login.data.decode("utf-8")
    assert 'Welcome, 001_club@gudlift.com' in html_response
    assert 'Competition 001' in html_response


def test_login_flow_failure(client, mock_clubs, mock_competitions):
    response_index = client.get("/")
    assert response_index.status_code == 200

    response_login = client.post("/showSummary",
                                 data={"email": "unknown@gudlift.com"})
    assert response_login.status_code == 401

    html_response = response_login.data.decode("utf-8")
    assert 'Welcome to the GUDLFT Registration Portal!' in html_response


def test_logout_flow_success(client, mock_clubs, mock_competitions):
    response_login = client.post("/showSummary",
                                 data={"email": "001_club@gudlift.com"})
    assert response_login.status_code == 200

    html_login = response_login.data.decode("utf-8")
    assert 'Welcome, 001_club@gudlift.com' in html_login
    assert 'Competition 001' in html_login

    response_logout = client.get("/logout", follow_redirects=True)
    assert response_logout.status_code == 200

    html_logout = response_logout.data.decode("utf-8")
    assert 'Welcome to the GUDLFT Registration Portal!' in html_logout
