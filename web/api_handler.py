import requests
import json
import rest_api.settings as settings


class ApiHandler:
    def __init__(self):
        self.api_url = "http://" + settings.host + ":" + str(settings.port)
        self.tasks_endpoint = "/api/tasks/"

    def get_tasks(self, status):
        if status.lower() == "active":
            payload = {"active": 1}
        elif status.lower() == "inactive":
            payload = {"active": 0}
        else:
            payload = {"active": 2}

        res = requests.get(self.api_url+self.tasks_endpoint, data=payload)
        results = json.loads(res.text)
        return results["results"]

    def save_session(self, start, end, cycles, task):
        payload = {
            "start": int(start),
            "end": int(end),
            "duration": int(end-start),
            "cycles": cycles,
            "task": task
        }
        res = requests.post(self.api_url + '/api/sessions/', data=payload)

