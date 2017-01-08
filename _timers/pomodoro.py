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

    def run_timer(self, duration, action):
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
                    self.screen.lcd_display_string(action
                                                   .center(16, ' '), 1)
                else:
                    self.pause()
                    self.screen.lcd_display_string(action + ' Paused'
                                                   .center(16, ' '), 1)
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

    def start_work(self):
        # TODO: Switch back to minutes
        print('Starting study')
        self.notify.toggle_led(self.notify.led_green, True)
        self.notify.toggle_led(self.notify.led_red, False)
        self.next_cycle = self.run_timer(self.study_t * 0, 'Work')

    def start_break(self, short):
        self.notify.toggle_led(self.notify.led_green, False)
        self.notify.toggle_led(self.notify.led_red, True)
        if short:
            print('Start short break')
            self.next_cycle = self.run_timer(self.short_break * 0, 'Break')
            self.cycle += 1
        else:
            print('Start long break')
            self.next_cycle = self.run_timer(self.long_break * 0, 'Break')
            self.cycle = 1

    def run_session(self):
        """Session loop, tracks sessions and start appropriate timers"""
        self.next_cycle = True
        while self.next_cycle:

            if self.cycle % 4 != 0:
                self.start_work()
                if self.next_cycle:
                    self.start_break(True)
                else:
                    break

            else:
                self.start_work()
                if self.next_cycle:
                    self.start_break(False)
                else:
                    break

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