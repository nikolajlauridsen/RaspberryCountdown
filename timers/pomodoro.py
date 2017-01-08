import RPi.GPIO as GPIO
import time
from .countdown import CountDown
from web.google_calendar import EventCreator


class PomodoroTimer(CountDown):
    """Pomodoro timer object"""

    def __init__(self, screen, notifier, buttons, study_length=25,
                 short_break=5, long_break=20, debug=False):
        # Inherit from countdown timer
        super().__init__()

        # And flags
        self.cycle = 1
        self.pomodoro_running = True
        self.next_cycle = True
        self.debug = debug

        # Initialize object
        self.screen = screen
        self.buttons = buttons
        self.notify = notifier
        self.calendar = EventCreator()

        # And integers
        if self.debug:
            minute_multiplier = 1
        else:
            minute_multiplier = 60
        self.study_t = study_length * minute_multiplier
        self.short_break = short_break * minute_multiplier
        self.long_break = long_break * minute_multiplier

    def run_timer(self, duration, action):
        """
        Run a timer
        Returns true if it expired and false if it was stopped
        """
        self.set_duration(duration)
        self.start()
        self.screen.lcd_display_string(action.center(16, ' '), 1)
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
        print('Starting study')
        self.notify.toggle_led(self.notify.led_green, True)
        self.notify.toggle_led(self.notify.led_red, False)
        self.next_cycle = self.run_timer(self.study_t, 'Work')

    def start_break(self, short):
        self.notify.toggle_led(self.notify.led_green, False)
        self.notify.toggle_led(self.notify.led_red, True)
        if short:
            print('Start short break')
            self.next_cycle = self.run_timer(self.short_break, 'Break')
            self.cycle += 1
        else:
            print('Start long break')
            self.next_cycle = self.run_timer(self.long_break, 'Break')
            self.cycle = 1

    def run_session(self):
        """Session loop, tracks sessions and start appropriate timers"""
        session_start = time.time()
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
        self.finish_session(session_start)

    def finish_session(self, session_start):
        # Session over TODO: make calendar event
        self.notify.clear_leds()
        self.screen.lcd_display_string('Session ended'.center(16, ' '), 1)
        self.screen.lcd_display_string(' ' * 16, 2)
        time.sleep(0.5)

        self.screen.lcd_display_string('Creating'.center(16, ' '), 1)
        self.screen.lcd_display_string('calendar event'.center(16, ' '), 2)
        session_end = time.time()
        if not self.debug:
            self.calendar.create_event('Pomodoro study session', session_start,
                                       session_end)

        self.screen.lcd_display_string('Session saved'.center(16, ' '), 1)
        self.screen.lcd_display_string(' ' * 16, 2)
        time.sleep(0.5)
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