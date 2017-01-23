import requests
import json
import rest_api.settings as settings


class ApiHandler:
    def __init__(self):
        self.api_url = "http://" + "127.0.0.1" + ":" + str(settings.port)
        self.tasks_endpoint = "/api/tasks/"

    def get_tasks(self):
        res = requests.get(self.api_url+self.tasks_endpoint)
        return json.loads(res.text)

    def save_session(self, start, end, cycles, task):
        payload = {
            "start": int(start),
            "end": int(end),
            "duration": int(end-start),
            "cycles": cycles,
            "task": task
        }
        res = requests.post(self.api_url + '/api/sessions/', data=payload)

