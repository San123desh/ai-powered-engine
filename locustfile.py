from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def test_suggestion(self):
        self.client.post(
            "/api/ai-engine",
            json={
                "action": "suggestion",
                "code": "def hello():",
                "context": {"language": "python"},
                "cursor_position": 10
            }
        )