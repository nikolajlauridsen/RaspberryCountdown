"""
  Copyright (C) 2017  Nikolaj Lauridsen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
        self.tracker_start = None   # Start time for the tracker

    def __repr__(self):
        return """Activity Tracker"""

    def finish_tracker(self, activity):
        """Finish a tracker session, saving it to the api database and
        creating a google calendar event, reset the stopwatch as well"""
        if self.tracker_start:
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
        self.notifier.clear_leds()
        self.reset()

    def reset(self):
        """Reset the stopwatch"""
        self.screen.lcd_display_string("Stopped".center(16), 1)
        self.screen.lcd_display_string(" " * 16, 2)
        self.elapsed = 0
        self.pause_data = []
        self.running = False
        self.tracker_start = None
        self.start_time = None

    def run_tracker(self, activity):
        """Run a tracker session, takes the name of the activity as a string"""
        # update screen
        if self.running:
            self.screen.lcd_display_string(activity.center(16), 1)
        else:
            self.screen.lcd_display_string("Paused".center(16), 1)
        self.screen.lcd_display_string(" "*16, 2)

        # Tracker loop
        while True:
            # Update the screen
            self.screen.lcd_display_string(self.get_elapsed_string().center(16, ' '), 2)

            if GPIO.event_detected(self.buttons['start']):

                if self.tracker_start:
                    # If the timer has been started, just toggle pause
                    self.toggle_pause(msg=activity['name'], leds=True)
                else:
                    # If it hasn't, set the tracking session start time
                    self.tracker_start = time.time()
                    # And then start the clock
                    self.notifier.toggle_led(self.notifier.led_green, True)
                    self.start(msg=activity['name'])

            elif GPIO.event_detected(self.buttons['stop']):
                # Finish the tracker, creating events and whatnot.
                self.finish_tracker(activity["name"])
                # Stop the tracking session
                break

    def main(self):
        """Main program for the activity tracker,
        will let the user pick an activity, and then runs a tracker with
        said ability"""

        # Fetch activities from API
        activities = self.api_handler.get_activities('active')

        # Cursor for pointing at an activity
        cursor = 0
        while True:
            # Update the screen
            self.screen.lcd_display_string("Choose activity", 1)
            self.screen.lcd_display_string(activities[cursor]["name"].center(16, ' '), 2)

            if GPIO.event_detected(self.buttons['start']):
                print('Starting activity tracker')
                # Run the selected activity
                self.run_tracker(activities[cursor])
                # Refresh activities list
                activities = self.api_handler.get_activities('active')

            elif GPIO.event_detected(self.buttons['forward']):
                # Move the cursor one up, unless it's at the edge, then reset
                if cursor < len(activities) - 1:
                    cursor += 1
                else:
                    cursor = 0

            elif GPIO.event_detected(self.buttons['back']):
                # Move the cursor one down, unless at..blah blah
                if cursor > 0:
                    cursor -= 1
                else:
                    cursor = len(activities)-1

            elif GPIO.event_detected(self.buttons['stop']):
                # Stop the main loop
                break

            time.sleep(0.2)
