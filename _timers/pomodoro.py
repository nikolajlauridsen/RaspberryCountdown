import RPi.GPIO as GPIO
import time
from .countdown import CountDown


class PomodoroTimer(CountDown):
    """Pomodoro timer object"""

    def __init__(self, screen, notifier, buttons, study_length=25,
                 short_break=5, long_break=20):
        # Inherit from countdown timer
        super().__init__()

        # Initialize object
        self.screen = screen
        self.buttons = buttons
        self.notify = notifier
        # And integers
        self.study_t = study_length
        self.short_break = short_break
        self.long_break = long_break

        # And flags
        self.cycle = 1
        self.pomodoro_running = True
        self.next_cycle = True

    def run_timer(self, duration):
        """
        Run a timer
        Returns true if it expired and false if it was stopped
        """
        self.set_duration(duration)
        self.start()
        while not self.check_expired():
            # Detect events
            if GPIO.event_detected(self.buttons['start']):
                if self.paused:
                    self.start()
                    self.screen.lcd_display_string('Session started '
                                                   .center(16, ' '), 1)
                else:
                    self.pause()
                    self.screen.lcd_display_string('Paused'.center(16, ' '), 1)
            elif GPIO.event_detected(self.buttons['stop']):
                # Stop the timer, return false, ie, no new cycle
                return False

            # Update time remaining on lcd
            self.screen.lcd_display_string(self.get_remaining_string()
                                           .center(16, ' '), 2)
            # Sleep
            time.sleep(0.2)

        # cycle finished, blink and start new
        self.notify.blink()
        return True

    def run_session(self):
        """Session loop, tracks sessions and start appropriate timers"""
        while self.next_cycle:
            if self.cycle % 4 != 0:
                # TODO: convert seconds to minutes (seconds works well for dev)
                print('Starting study')
                self.next_cycle = self.run_timer(self.study_t*60)
                print('Start short break')
                self.next_cycle = self.run_timer(self.short_break*60)
                self.cycle += 1
            else:
                print('Starting study')
                self.next_cycle = self.run_timer(self.study_t*60)
                print('Start long break')
                self.next_cycle = self.run_timer(self.long_break*60)
                self.cycle = 1

        # Session over TODO: make calendar event
        print('Session finished')

    def main(self):
        """Main loop, displays title and awaits input, then runs a session"""
        while self.pomodoro_running:
            self.screen.lcd_display_string('Pomodoro Timer'.center(16, ' '), 1)
            self.screen.lcd_display_string('Press start'.center(16, ' '), 2)

            if GPIO.event_detected(self.buttons['start']):
                print('session')
                self.run_session()

            elif GPIO.event_detected(self.buttons['stop']):
                print('Pomodoro stopped')
                break

        time.sleep(0.2)