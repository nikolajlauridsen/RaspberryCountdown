import requests
import json


class ApiHandler:
    def __init__(self):
        self.api_ip = "0.0.0.0"
        self.api_port = "3000"
        self.api_url = "http://" + self.api_ip + ":" + self.api_port
        # Endpoint shorthands, makes everything a bit prettier
        self.tasks = "/api/tasks/"
        self.session = "/api/sessions/"
        self.activities = "/api/activities/"
        self.tracker = "/api/timetrack/"

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

    def get_activities(self, status):
        """Get all activities from the api database
        takse a status string of either 'active', 'inactive', or 'both"""
        if status.lower() == "active":
            payload = {"active": 1}
        elif status.lower() == "inactive":
            payload = {"active": 0}
        else:
            payload = {"active": 2}

        res = requests.get(self.api_url + self.activities, data=payload)
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

    def save_tracker(self, start, end, duration, activity):
        payload = {
            "start": int(start),
            "end": int(end),
            "duration": int(duration),
            "activity": activity
        }
        res = requests.post(self.api_url + self.tracker, data=payload)

