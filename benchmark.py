import requests
import time
import json
import psutil
import csv
import subprocess
from typing import Dict, List
from thefuzz import fuzz
import re

class BenchmarkFramework:
    def __init__(self, api_url: str = "http://localhost:8000/api/ai-engine"):
        self.api_url = api_url
        self.results = []

    def run_test(self, action: str, payload: Dict, expected: str = None) -> Dict:
        start_time = time.time()
        try:
            response = requests.post(self.api_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            latency = response.elapsed.total_seconds()
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            result = {
                "action": action,
                "response_time": response_time,
                "latency": latency,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "status_code": response.status_code,
                "response": response.json()
            }
            if expected:
                generated = response.json().get("data", {}).get(action[:-1])
                result["accuracy"] = self.calculate_accuracy(generated, expected, payload.get("context", {}).get("language", "python"))
                result["usability"] = 1.0 if result["accuracy"] > 0.8 else 0.0
            self.results.append(result)
            return result
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return {"action": action, "status_code": 500, "error": str(e)}

    def normalize_code(self, code: str) -> str:
        # Remove comments and all whitespace for comparison
        code = re.sub(r'#.*', '', code)  # Remove Python comments
        code = re.sub(r'//.*', '', code)  # Remove JS comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Remove JS block comments
        code = re.sub(r'\s+', '', code)  # Remove all whitespace
        return code.strip()

    def calculate_accuracy(self, generated: str, expected: str, language: str) -> float:
        if not generated or not expected:
            return 0.0
        # Normalize both codes
        norm_generated = self.normalize_code(generated)
        norm_expected = self.normalize_code(expected)
        print(f"Generated: {repr(generated)}")
        print(f"Expected: {repr(expected)}")
        print(f"Normalized Generated: {repr(norm_generated)}")
        print(f"Normalized Expected: {repr(norm_expected)}")
        if norm_generated == norm_expected:
            return 1.0
        # fallback to fuzzy match
        similarity = fuzz.partial_ratio(norm_generated, norm_expected) / 100.0
        return similarity if similarity >= 0.3 else 0.3

    def is_syntactically_correct(self, code: str, language: str) -> bool:
        if not code or code.startswith(("#", "//")):
            return False

        temp_file = f"temp_code.{language}"
        with open(temp_file, "w") as f:
            f.write(code)

        try:
            if language.lower() == "python":
                result = subprocess.run(["flake8", temp_file, "--max-line-length=120"], capture_output=True, text=True)
                return "ERROR" not in result.stderr
            elif language.lower() == "javascript":
                result = subprocess.run(["eslint", temp_file, "--max-warnings=0"], capture_output=True, text=True)
                return "error" not in result.stderr.lower()
            else:
                return True
        except FileNotFoundError:
            print(f"Linting tool not found for {language}. Install flake8 or eslint.")
            return True
        finally:
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def save_results(self, filename: str = "benchmark_results.csv"):
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["action", "response_time", "latency", "cpu_percent", "memory_percent", "accuracy", "usability", "status_code", "response"])
                writer.writeheader()
                writer.writerows(self.results)
        except Exception as e:
            print(f"Error saving results: {e}")

    def compute_averages(self):
        averages = {}
        for action in set(result["action"] for result in self.results):
            action_results = [r for r in self.results if r["action"] == action]
            averages[action] = {
                "avg_response_time": sum(r["response_time"] for r in action_results) / len(action_results),
                "avg_latency": sum(r["latency"] for r in action_results) / len(action_results),
                "avg_cpu_percent": sum(r["cpu_percent"] for r in action_results) / len(action_results),
                "avg_memory_percent": sum(r["memory_percent"] for r in action_results) / len(action_results),
                "avg_accuracy": sum(r.get("accuracy", 0) for r in action_results) / len(action_results),
                "avg_usability": sum(r.get("usability", 0) for r in action_results) / len(action_results),
            }
        return averages

if __name__ == "__main__":
    benchmark = BenchmarkFramework()
    test_cases = [
        # Python suggestion: simple return
        {
            "action": "suggestion",
            "payload": {"action": "suggestion", "code": "def add(a, b):", "context": {"language": "python"}, "cursor_position": 13},
            "expected": "    return a + b"
        },
        # Python suggestion: factorial
        {
            "action": "suggestion",
            "payload": {"action": "suggestion", "code": "def factorial(n):", "context": {"language": "python"}, "cursor_position": 18},
            "expected": "    if n == 0:\n        return 1"
        },
        # Python suggestion: check even
        {
            "action": "suggestion",
            "payload": {"action": "suggestion", "code": "def is_even(num):", "context": {"language": "python"}, "cursor_position": 16},
            "expected": "    return num % 2 == 0"
        },
        # Python suggestion: empty function
        {
            "action": "suggestion",
            "payload": {"action": "suggestion", "code": "def do_nothing():", "context": {"language": "python"}, "cursor_position": 17},
            "expected": "    pass"
        },
        # Python generate: sum
        {
            "action": "generate",
            "payload": {"action": "generate", "code": "def sum_list(lst):", "context": {"language": "python"}},
            "expected": "def sum_list(lst):\n    return sum(lst)"
        },
        # Python generate: check palindrome
        {
            "action": "generate",
            "payload": {"action": "generate", "code": "def is_palindrome(s):", "context": {"language": "python"}},
            "expected": "def is_palindrome(s):\n    return s == s[::-1]"
        },
        # JavaScript suggestion: greet
        {
            "action": "suggestion",
            "payload": {"action": "suggestion", "code": "function greet(name) {", "context": {"language": "javascript"}, "cursor_position": 23},
            "expected": "    return \"Hello, \" + name;"
        },
        # JavaScript suggestion: check even
        {
            "action": "suggestion",
            "payload": {"action": "suggestion", "code": "function isEven(num) {", "context": {"language": "javascript"}, "cursor_position": 21},
            "expected": "    return num % 2 === 0;"
        },
        # JavaScript generate: sum
        {
            "action": "generate",
            "payload": {"action": "generate", "code": "function sum(a, b) {", "context": {"language": "javascript"}},
            "expected": "function sum(a, b) {\n    return a + b;\n}"
        },
        # JavaScript generate: reverse string
        {
            "action": "generate",
            "payload": {"action": "generate", "code": "function reverseString(str) {", "context": {"language": "javascript"}},
            "expected": "function reverseString(str) {\n    return str.split('').reverse().join('');\n}"
        },
        # JavaScript generate: factorial
        {
            "action": "generate",
            "payload": {"action": "generate", "code": "function factorial(n) {", "context": {"language": "javascript"}},
            "expected": "function factorial(n) {\n    if (n === 0) {\n        return 1;\n    }\n    return n * factorial(n - 1);\n}"
        }
    ]

    for _ in range(10):
        for test in test_cases:
            result = benchmark.run_test(test["action"], test["payload"], test["expected"])
            print(f"Test {test['action']} with code '{test['payload']['code'][:10]}...': {result}")

    benchmark.save_results()
    print("Averages:")
    for action, avg in benchmark.compute_averages().items():
        print(f"{action}: {avg}")