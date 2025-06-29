from locust import HttpUser, task, between

class AIEngineUser(HttpUser):
    wait_time = between(1, 3)  # seconds between tasks

    @task(2)
    def python_suggestion(self):
        self.client.post("/api/ai-engine", json={
            "action": "suggestion",
            "code": "def add(a, b):",
            "context": {"language": "python"},
            "cursor_position": 13
        })

    @task(2)
    def python_generate(self):
        self.client.post("/api/ai-engine", json={
            "action": "generate",
            "code": "def is_even(num):",
            "context": {"language": "python"}
        })

    @task(1)
    def js_suggestion(self):
        self.client.post("/api/ai-engine", json={
            "action": "suggestion",
            "code": "function sum(a, b) {",
            "context": {"language": "javascript"},
            "cursor_position": 20
        })

    @task(1)
    def js_generate(self):
        self.client.post("/api/ai-engine", json={
            "action": "generate",
            "code": "function isEven(num) {",
            "context": {"language": "javascript"}
        })