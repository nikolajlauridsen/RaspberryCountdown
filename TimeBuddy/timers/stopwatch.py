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

    def start(self, msg="Running"):
        print("clock started")
        self.screen.lcd_display_string(msg.center(16), 1)
        self.start_time = time.time()
        self.running = True

    def reset(self):
        self.screen.lcd_display_string("Stopped".center(16), 1)
        self.screen.lcd_display_string(" "*16, 2)
        self.elapsed = 0
        self.pause_data = []
        self.running = False

    def toggle_pause(self, msg="Running"):
        if self.running:
            print("clock paused")
            self.screen.lcd_display_string("Paused".center(16), 1)
            self.pause_data.append(time.time() - self.start_time)
            self.running = False
        else:
            self.start(msg=msg)

    def get_elapsed(self):
        if self.running:
            elapsed = time.time() - self.start_time
        else:
            elapsed = 0

        for duration in self.pause_data:
            elapsed += duration
        return elapsed

    def get_elapsed_string(self):
        elapsed = self.get_elapsed()

        if 60 < elapsed < 3600:
            mins = elapsed // 60
            s = elapsed % 60
            return "{:02}:{:02}".format(int(mins), int(s))

        elif elapsed > 3600:
            hrs = elapsed // 3600
            hrs_remainder = elapsed % 3600
            mins = hrs_remainder // 60
            s = hrs_remainder % 60
            return "{:02}:{:02}:{:02}".format(int(hrs), int(mins), int(s))

        else:
            return "{:02}".format(int(elapsed))

    def main(self):
        if self.running:
            self.screen.lcd_display_string("Running".center(16), 1)
        else:
            self.screen.lcd_display_string("Stopped".center(16), 1)
        self.screen.lcd_display_string(" "*16, 2)

        while True:
            self.screen.lcd_display_string(self.get_elapsed_string(), 2)
            if GPIO.event_detected(self.buttons["start"]):
                if self.start_time:
                    self.toggle_pause()
                else:
                    self.start()

            if GPIO.event_detected(self.buttons['back']):
                self.reset()

            if GPIO.event_detected(self.buttons['stop']):
                break
            time.sleep(0.2)


