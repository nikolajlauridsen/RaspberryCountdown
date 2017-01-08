import time

import RPi.GPIO as GPIO

from timers.pomodoro import PomodoroTimer
from physical.notifier import Notifier
from physical import LCD_driver as lcdDriver

# Buttons dictionary
buttons = {
    'start': 23,
    'stop': 24
}

# Output dictionary for notifier (lcd screen has its own class)
output = {
    'buzzer': 22,
    'green_led': 27,
    'red_led': 17
}

# Set up channels
GPIO.setmode(GPIO.BCM)
GPIO.setup(buttons['start'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buttons['stop'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(buttons['start'], GPIO.RISING)
GPIO.add_event_detect(buttons['stop'], GPIO.RISING)

# Initialize objects
screen = lcdDriver.lcd()
notifier = Notifier(output)
pomodoro = PomodoroTimer(screen, notifier, buttons, debug=False)

pomodoro.main()

# Program finished
screen.lcd_clear()
screen.lcd_display_string('Program ended'.center(16, '~'), 1)
notifier.blink()
# Cleanup
notifier.clean()
GPIO.cleanup(23)
GPIO.cleanup(24)
print('Timer finished')
