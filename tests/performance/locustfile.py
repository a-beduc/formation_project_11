from locust import HttpUser, task, constant_throughput


class ProjectPerfTest(HttpUser):
    wait_time = constant_throughput(10)
    competition = {"name": "Spring Festival",
                   "date": "2030-03-27 10:00:00",
                   "numberOfPlaces": 25}
    club = {"name": "Simply Lift",
            "email": "john@simplylift.co",
            "points": 13}

    @task
    def index(self):
        self.client.get("/")

    @task
    def login(self):
        self.client.post('/showSummary', data={"email": self.club['email']})

    @task(2)
    def purchase_places(self):
        self.client.post('/purchasePlaces',
                         data={"competition": self.competition['name'],
                               "club": self.club['name'],
                               "places": 0})

    @task
    def board(self):
        self.client.get('/board')

    @task(2)
    def book(self):
        self.client.get(
            f'/book/{self.competition['name']}/{self.club["name"]}')
