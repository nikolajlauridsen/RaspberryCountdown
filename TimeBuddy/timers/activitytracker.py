from .stopwatch import StopWatch
import RPi.GPIO as GPIO
from web.google_calendar import EventCreator
from web.api_handler import ApiHandler
import time


class ActivityTracker(StopWatch):

    def __init__(self, screen, notifier, buttons):
        super().__init__(screen, notifier, buttons)
        self.api_handler = ApiHandler()
        self.calendar = EventCreator()
        self.tracker_start = None

    def __repr__(self):
        return """Activity Tracker"""

    def finish_tracker(self, activity):
        end = time.time()
        duration = self.get_elapsed()
        self.screen.lcd_display_string('Saving event'.center(16, ' '), 2)
        self.api_handler.save_tracker(self.tracker_start, end,
                                      duration, activity)
        summary = "Activity tracker session"
        description = "Activity: {}\nDuration: {}".format(activity, self.get_elapsed_string())
        self.screen.lcd_display_string('calendar event'.center(16, ' '), 2)
        self.calendar.create_event(summary,
                                   self.tracker_start, end,
                                   description=description)

    def reset(self):
        self.screen.lcd_display_string("Stopped".center(16), 1)
        self.screen.lcd_display_string(" " * 16, 2)
        self.elapsed = 0
        self.pause_data = []
        self.running = False
        self.tracker_start = None
        self.start_time = None

    def run_tracker(self, activity):
        # update screen
        if self.running:
            self.screen.lcd_display_string(activity.center(16), 1)
        else:
            self.screen.lcd_display_string("Paused".center(16), 1)
        self.screen.lcd_display_string(" "*16, 2)

        # Tracker loop
        while True:
            self.screen.lcd_display_string(self.get_elapsed_string().center(16, ' '), 2)
            if GPIO.event_detected(self.buttons['start']):
                if self.start_time:
                    self.toggle_pause(msg=activity['name'])
                else:
                    self.tracker_start = time.time()
                    self.start(msg=activity['name'])

            elif GPIO.event_detected(self.buttons['stop']):
                self.finish_tracker(activity["name"])
                self.reset()
                break

    def main(self):
        activities = self.api_handler.get_activities('active')

        cursor = 0
        while True:
            self.screen.lcd_display_string("Choose activity", 1)
            self.screen.lcd_display_string(activities[cursor]["name"].center(16, ' '), 2)

            if GPIO.event_detected(self.buttons['start']):
                print('Starting activity tracker')
                self.run_tracker(activities[cursor])
                activities = self.api_handler.get_activities('active')

            elif GPIO.event_detected(self.buttons['forward']):
                if cursor < len(activities) - 1:
                    cursor += 1
                else:
                    cursor = 0

            elif GPIO.event_detected(self.buttons['back']):
                if cursor > 0:
                    cursor -= 1
                else:
                    cursor = len(activities)-1

            elif GPIO.event_detected(self.buttons['stop']):
                break

            time.sleep(0.2)
