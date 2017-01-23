import RPi.GPIO as GPIO
import time
from .countdown import CountDown
from web.google_calendar import EventCreator
from web.api_handler import ApiHandler


class PomodoroTimer(CountDown):
    """Pomodoro timer object"""

    def __init__(self, screen, notifier, buttons, study_length=25,
                 short_break=5, long_break=20, debug=False):
        # Inherit from countdown timer
        super().__init__()

        # And flags
        self.cycle = 1
        self.total_cycles = 0
        self.pomodoro_running = True
        self.next_cycle = True
        self.debug = debug

        # Initialize object
        self.screen = screen
        self.buttons = buttons
        self.notify = notifier
        self.calendar = EventCreator()
        self.api_handler = ApiHandler()

        # And integers
        if self.debug:
            minute_multiplier = 1
        else:
            minute_multiplier = 60
        self.study_t = study_length * minute_multiplier
        self.short_break = short_break * minute_multiplier
        self.long_break = long_break * minute_multiplier

    def __repr__(self):
        return "Pomodoro"

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
        self.notify.beep(count=2, beep=0.2, pause=0.1)
        return True

    def await_confirmation(self, message):
        """Awaits confirmation from user returns true/false"""
        self.screen.lcd_display_string(message.center(16, ' '), 1)
        self.screen.lcd_display_string('Press start'.center(16, ' '), 2)
        while not GPIO.event_detected(self.buttons['start']):
            if GPIO.event_detected(self.buttons['stop']):
                return False
            time.sleep(0.2)
        return True

    def start_work(self):
        print('Starting study')
        self.total_cycles += 1
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

    def run_session(self, task):
        """Session loop, tracks sessions and start appropriate timers"""
        session_start = time.time()
        self.next_cycle = True
        while self.next_cycle:
            self.next_cycle = self.await_confirmation('Confirm work')
            if not self.next_cycle: break

            if self.cycle % 4 != 0:
                self.start_work()
                if self.next_cycle:
                    self.next_cycle = self.await_confirmation('Confirm break')
                    if not self.next_cycle: break
                    self.start_break(True)
                else:
                    break

            else:
                self.start_work()
                if self.next_cycle:
                    self.next_cycle = self.await_confirmation('Confirm break')
                    if not self.next_cycle: break
                    self.start_break(False)
                else:
                    break
        self.finish_session(session_start, task)

    def finish_session(self, session_start, task):
        # Session over
        self.notify.clear_leds()
        self.screen.lcd_display_string('Session ended'.center(16, ' '), 1)
        self.screen.lcd_display_string(' ' * 16, 2)
        time.sleep(0.5)

        self.screen.lcd_display_string('Creating'.center(16, ' '), 1)
        self.screen.lcd_display_string('calendar event'.center(16, ' '), 2)
        session_end = time.time()
        if not self.debug:
            duration = session_end-session_start
            if duration > 10:
                stamp = self.seconds_to_timestamp(duration)
                description = 'Duration: ' + stamp + '\n' + 'Task: ' + task
                self.calendar.create_event('Pomodoro study session', session_start,
                                           session_end, description)
                self.api_handler.save_session(session_start, session_end,
                                              self.total_cycles, task)

            self.screen.lcd_display_string('Session saved'.center(16, ' '), 1)
            self.screen.lcd_display_string(' ' * 16, 2)
        self.total_cycles = 0
        time.sleep(0.5)
        print('Session finished')

    def main(self):
        """Main loop, displays title and awaits input, then runs a session"""
        tasks = self.api_handler.get_tasks()
        cursor = 0
        while GPIO.input(self.buttons["stop"]) == GPIO.HIGH:
            self.screen.lcd_display_string('Choose task'.center(16, ' '), 1)
            self.screen.lcd_display_string(tasks[cursor]["name"].center(16, ' '), 2)

            if GPIO.event_detected(self.buttons['start']):
                print('session')
                self.run_session(tasks[cursor]["name"])

            elif GPIO.event_detected(self.buttons['forward']):
                if cursor < len(tasks)-1:
                    cursor += 1
                else:
                    cursor = 0

            elif GPIO.event_detected(self.buttons['back']):
                if cursor > 0:
                    cursor -= 1
                else:
                    cursor = len(tasks)-1

        time.sleep(0.2)
