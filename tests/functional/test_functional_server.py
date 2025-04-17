"""
Integration tests for the main Flask application defined in server.py

This module tests the login and logout functionalities

Fixtures such as 'client', 'mock_clubs', 'mock_competitions' are defined
in a 'conftest.py' file and injected by pytest during test.
"""


import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from server import app as flask_app


class TestServerFunctional:
    """
    This class test a few scenarios where a fictive user interacts with
    the application.
    A local server is started in a second thread at the beginning of the
    test suite.
    """
    @classmethod
    def setup_class(cls):
        """
        Starts the Flask app in a background thread and opens a Firefox
        browser session controlled by Selenium.
        """
        cls.server_thread = threading.Thread(target=cls.start_flask_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)
        cls.driver = webdriver.Firefox()
        cls.driver.implicitly_wait(2)

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()

    def setup_method(self, method):
        self.driver.get("http://127.0.0.1:5000")

    @staticmethod
    def start_flask_server():
        flask_app.run(host='127.0.0.1', port=5000)

    def get_flash_message(self):
        error_block = self.driver.find_element(By.ID, "error-messages")
        return [msg.text for msg in
                error_block.find_elements(By.TAG_NAME, 'li')]

    def test_link_to_board_page_and_content(self):
        # Find the link to the board and click it
        board_link = self.driver.find_element(By.LINK_TEXT,
                                              "Club Points Board")
        board_link.click()
        assert self.driver.current_url == "http://127.0.0.1:5000/board"

        # Find the link to the index and click it
        index_link = self.driver.find_element(By.LINK_TEXT,
                                              "Back to login")
        index_link.click()
        assert self.driver.current_url == "http://127.0.0.1:5000/"

    def test_login_page_wrong_email(self):
        email_input = self.driver.find_element(By.ID, "email")
        button = self.driver.find_element(By.ID, "form-button")
        email_input.send_keys("wrong@email.com")
        button.click()
        assert "The provided email is not valid." in self.get_flash_message()
        assert self.driver.current_url == "http://127.0.0.1:5000/showSummary"

    def test_login_page_then_logout(self):
        email_input = self.driver.find_element(By.ID, "email")
        button = self.driver.find_element(By.ID, "form-button")
        email_input.send_keys("001_club@gudlift.com")
        button.click()
        logout_link = self.driver.find_element(By.LINK_TEXT, "Logout")
        logout_link.click()

    def test_purchase_too_many_places_then_enough_places_then_check_board(
            self):
        # Log in as Club 001
        email_input = self.driver.find_element(By.ID, "email")
        email_input.send_keys("001_club@gudlift.com")
        button = self.driver.find_element(By.ID, "form-button")
        button.click()
        assert self.driver.current_url == "http://127.0.0.1:5000/showSummary"

        # Click on link to the Competition 2
        competition_two_link = self.driver.find_element(
            By.CSS_SELECTOR,
            'a[href="/book/Competition%20002/Club%20001"]')
        competition_two_link.click()
        assert (self.driver.current_url ==
                "http://127.0.0.1:5000/book/Competition%20002/Club%20001")

        # Try to purchase 10 places
        places_input = self.driver.find_element(By.ID, "places")
        button = self.driver.find_element(By.TAG_NAME, "button")
        places_input.send_keys("10")
        button.click()
        assert (self.driver.current_url ==
                "http://127.0.0.1:5000/purchasePlaces")
        assert (("Not enough available places for this competition. "
                "Requested : 10, still available : 4") in
                self.get_flash_message())

        # Purchase 4 places
        places_input = self.driver.find_element(By.ID, "places")
        button = self.driver.find_element(By.TAG_NAME, "button")
        places_input.send_keys("4")
        button.click()
        error_messages = self.driver.find_element(By.ID, "error-messages")
        flash_messages = error_messages.find_elements(By.TAG_NAME, "li")
        assert (self.driver.current_url ==
                "http://127.0.0.1:5000/purchasePlaces")
        assert ("Great-booking complete!" in
                [msg.text for msg in flash_messages])

        # log out
        logout_link = self.driver.find_element(By.LINK_TEXT, "Logout")
        logout_link.click()
        assert self.driver.current_url == "http://127.0.0.1:5000/"

        # Click on link to board
        board_link = self.driver.find_element(By.LINK_TEXT,
                                              "Club Points Board")
        board_link.click()
        assert self.driver.current_url == "http://127.0.0.1:5000/board"

        # Verify that club points has been updated
        cells = self.driver.find_elements(By.TAG_NAME, "td")
        for index in range(len(cells) - 1):
            if cells[index].text == 'Club 001':
                assert cells[index + 1].text == '9'
                break
