import requests
import rest_api.settings as settings


class ApiHandler:
    def __init__(self):
        self.api_url = "http://" + settings.host + ":" + str(settings.port)

    def save_session(self, start, end, cycles):
        payload = {
            "start": int(start),
            "end": int(end),
            "duration": int(end-start),
            "cycles": cycles
        }
        res = requests.post(self.api_url + '/api/sessions/', data=payload)
