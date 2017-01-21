import time
import RPi.GPIO as GPIO


class StopWatch:

    def __init__(self, screen, notifier, buttons):
        self.start_time = None
        self.elapsed = None
        self.pause_data = []
        self.running = False
        self.screen = screen
        self.buttons = buttons
        self.notifier = notifier

    def __repr__(self):
        return "StopWatch"

    def start(self):
        print("clock started")
        self.screen.lcd_display_string("Running".center(16), 1)
        self.start_time = time.time()
        self.running = True

    def toggle_pause(self):
        if self.running:
            print("clock paused")
            self.screen.lcd_display_string("Paused".center(16), 1)
            self.pause_data.append(self.get_elapsed())
            self.running = False
        else:
            self.start()

    def get_elapsed(self):
        return time.time() - self.start_time

    def get_elapsed_string(self, precision=2):
        if self.running:
            elapsed = self.get_elapsed()
        else:
            elapsed = 0
        for duration in self.pause_data:
            elapsed += duration

        if 60 < elapsed < 3600:
            mins = elapsed // 60
            s = elapsed % 60
            return "{}:{}".format(int(mins), round(s, precision))

        elif elapsed > 3600:
            hrs = elapsed // 3600
            hrs_remainder = elapsed % 3600
            mins = hrs_remainder // 60
            s = hrs_remainder % 60
            return "{}:{}:{}".format(int(hrs), int(mins), round(s, precision))

        else:
            return "{}".format(round(elapsed, precision))

    def main(self):
        self.screen.lcd_display_string("Timer stopped".center(16), 1)
        self.screen.lcd_display_string(" "*16, 2)

        GPIO.wait_for_edge(self.buttons["start"], GPIO.RISING)
        self.start()
        self.screen.lcd_display_string("Running", 1)

        while GPIO.input(self.buttons["stop"]) == GPIO.HIGH:
            self.screen.lcd_display_string(self.get_elapsed_string(), 2)
            if GPIO.event_detected(self.buttons["start"]):
                self.toggle_pause()
            time.sleep(0.2)


