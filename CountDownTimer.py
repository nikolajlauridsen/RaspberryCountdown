import LCD_driver as lcdDriver
from countdown import CountDown
from notifier import Notifier
import RPi.GPIO as GPIO
import time

# Button shorthands
start_bth = 23
stop_btn = 24

# Set up channels
GPIO.setmode(GPIO.BCM)
GPIO.setup(start_bth, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(stop_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(start_bth, GPIO.RISING)
GPIO.add_event_detect(stop_btn, GPIO.RISING)

# Initialize objects
timer = CountDown()
screen = lcdDriver.lcd()
notifier = Notifier(22, 27, 17)

# Update LCD and wait for input TODO: do this with physical buttons
screen.lcd_display_string('Waiting'.center(16, '~'), 1)
screen.lcd_display_string('Input duration'.center(16, '~'), 2)
duration = int(input('Input duraion: '))
timer.set_duration(duration)
screen.lcd_display_string('Press start'.center(16, '~'), 1)
screen.lcd_display_string(timer.get_remaining_string().center(16, ' '), 2)

# Main loop
while not timer.check_expired():
    # Detect events
    if GPIO.event_detected(start_bth):
        if timer.paused:
            timer.start()
            screen.lcd_display_string('Running'.center(16, '~'), 1)
        else:
            timer.pause()
            screen.lcd_display_string('Paused'.center(16, '~'), 1)
    # Update time remaining row on LCD 
    screen.lcd_display_string(timer.get_remaining_string().center(16, ' '), 2)
    # Sleep for a little while, no reason to overstress the CPU
    time.sleep(0.2)

# Timer finished, notify via blinks
screen.lcd_display_string('Timer finished'.center(16, '~'), 1)
notifier.blink()
# Cleanup
notifier.clean()
GPIO.cleanup(23)
GPIO.cleanup(24)
print('Timer finished')
