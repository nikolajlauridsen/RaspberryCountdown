import requests
import json
import rest_api.settings as settings


class ApiHandler:
    def __init__(self):
        self.api_url = "http://" + settings.host + ":" + str(settings.port)
        # Endpoint shorthands, makes everything a bit prettier
        self.tasks = "/api/tasks/"
        self.session = "/api/sessions"

    def get_tasks(self, status):
        """Get all tasks from the api database
        takes a status string of either 'active', 'inactive', or 'both'"""
        if status.lower() == "active":
            payload = {"active": 1}
        elif status.lower() == "inactive":
            payload = {"active": 0}
        else:
            payload = {"active": 2}

        res = requests.get(self.api_url + self.tasks, data=payload)
        results = json.loads(res.text)
        return results["results"]

    def save_session(self, start, end, cycles, task):
        """Insert a pomodoro session into the database"""
        payload = {
            "start": int(start),
            "end": int(end),
            "duration": int(end-start),
            "cycles": cycles,
            "task": task
        }
        res = requests.post(self.api_url + self.session, data=payload)

