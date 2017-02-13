import time

import RPi.GPIO as GPIO

from timers.pomodoro import PomodoroTimer
from timers.stopwatch import StopWatch
from physical.notifier import Notifier
from physical import LCD_driver as lcdDriver

# Buttons dictionary
buttons = {
    'start': 23,
    'stop': 24,
    'back': 6,
    'forward': 5
}

# Output dictionary for notifier (lcd screen has its own class)
output = {
    'buzzer': 22,
    'green_led': 27,
    'red_led': 17
}

if __name__ == "__main__":
    # Set up channels
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buttons['start'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttons['stop'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttons['back'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buttons['forward'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # All switches are equal, but some are more equal than others,
    # a bounce on the stop button can be a major hassle, while it's not as
    # big an issue on back/forward, less bouncetime makes back/forward feel more
    # responsive as well.
    GPIO.add_event_detect(buttons['start'], GPIO.RISING, bouncetime=300)
    GPIO.add_event_detect(buttons['stop'], GPIO.RISING, bouncetime=500)
    GPIO.add_event_detect(buttons['back'], GPIO.RISING, bouncetime=200)
    GPIO.add_event_detect(buttons['forward'], GPIO.RISING, bouncetime=200)

    # Initialize objects
    screen = lcdDriver.lcd()
    notifier = Notifier(output)
    pomodoro = PomodoroTimer(screen, notifier, buttons, debug=False)
    stopwatch = StopWatch(screen, notifier, buttons)

    options = [pomodoro, stopwatch]

    cursor = 0
    while True:
        screen.lcd_display_string("Select program".center(16), 1)
        screen.lcd_display_string(str(options[cursor]).center(16), 2)

        if GPIO.event_detected(buttons['forward']):
            if cursor < len(options)-1:
                cursor += 1
            else:
                cursor = 0

        elif GPIO.event_detected(buttons['back']):
            if cursor > 0:
                cursor -= 1
            else:
                cursor = len(options)-1

        elif GPIO.event_detected(buttons['start']):
            options[cursor].main()

        elif GPIO.event_detected(buttons['stop']):
            break

        time.sleep(0.2)

    # Program finished
    screen.lcd_clear()
    screen.lcd_display_string('Program ended'.center(16, '~'), 1)
    notifier.blink()
    # Cleanup
    notifier.clean()
    for button in buttons.values():
        GPIO.cleanup(button)
    print('Timer finished')
