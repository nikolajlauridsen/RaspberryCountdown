import RPi.GPIO as GPIO
import time


class Notifier:
    def __init__(self, output):
        self.beeper = output["buzzer"]
        self.led_green = output["green_led"]
        self.led_red = output["red_led"]
        GPIO.setup(self.beeper, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.led_green, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.led_red, GPIO.OUT, initial=GPIO.LOW)

    def beep(self, beep=0.4, pause=0.2, count=5):
        for i in range(count):
            GPIO.output(self.beeper, GPIO.HIGH)
            time.sleep(beep)
            GPIO.output(self.beeper, GPIO.LOW)
            time.sleep(pause)

    def clean(self):
        GPIO.cleanup(self.beeper)
        GPIO.cleanup(self.led_green)
        GPIO.cleanup(self.led_red)

    def blink(self, color='both', alternate=True, cycles=5):
        if color == 'both' and alternate:
            for n in range(cycles):
                GPIO.output(self.led_red, GPIO.LOW)
                GPIO.output(self.led_green, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.led_green, GPIO.LOW)
                GPIO.output(self.led_red, GPIO.HIGH)
                time.sleep(0.2)
            GPIO.output(self.led_red, GPIO.LOW)

    @staticmethod
    def toggle_led(led, state):
        if state:
            GPIO.output(led, GPIO.HIGH)
        else:
            GPIO.output(led, GPIO.LOW)

    def clear_leds(self):
        GPIO.output(self.led_green, GPIO.LOW)
        GPIO.output(self.led_red, GPIO.LOW)
