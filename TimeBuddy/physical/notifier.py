"""
  Copyright (C) 2017  Nikolaj Lauridsen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import RPi.GPIO as GPIO
import time
import threading


class Notifier:
    def __init__(self, output):
        self.beeper = output["buzzer"]
        self.led_green = output["green_led"]
        self.led_red = output["red_led"]
        GPIO.setup(self.beeper, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.led_green, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.led_red, GPIO.OUT, initial=GPIO.LOW)

    def __repr__(self):
        return """Notifier object handling 2 LEDs and a buzzer."""

    def beep(self, beep=0.4, pause=0.2, count=5):
        """Beep the buzzer, takes 3 kwargs:
        beep=int  - time the buzzer is on in seconds
        pause=int - time the buzzer is resting between beeps in seconds
        count=int - amount of beeps"""
        for i in range(count):
            GPIO.output(self.beeper, GPIO.HIGH)
            time.sleep(beep)
            GPIO.output(self.beeper, GPIO.LOW)
            time.sleep(pause)

    def clean(self):
        """Cleanup the GPIOs used by notifier"""
        GPIO.cleanup(self.beeper)
        GPIO.cleanup(self.led_green)
        GPIO.cleanup(self.led_red)

    def blink(self, color='both', alternate=True, cycles=5):
        """Blink the two LEDS.
        Takes 3 kwargs:
        color = 'both', 'red', or 'green' determines which color to blink,
        default is both
        alternate=Bool, set the colors to alternate or not, default is true
        cycles=int, amount of blink cycles, default is 5"""
        # TODO: Finish this function proper
        if color == 'both' and alternate:
            for n in range(cycles):
                GPIO.output(self.led_red, GPIO.LOW)
                GPIO.output(self.led_green, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.led_green, GPIO.LOW)
                GPIO.output(self.led_red, GPIO.HIGH)
                time.sleep(0.2)
            GPIO.output(self.led_red, GPIO.LOW)

    def notify(self, blinks=5, beeps=2):
        """Utilize threading to beep and blink at the same time.
        Takes 2 kwargs:
        blinks=int - Amount of blink cycles (1 red & 1 green flash = 1 cycle)
        beeps=int  - Amount of beeps
        """
        blink_thread = threading.Thread(target=self.blink,
                                        kwargs={"cycles": blinks})

        beep_thread = threading.Thread(target=self.beep,
                                       kwargs={"count": beeps,
                                               "beep": 0.2,
                                               "pause": 0.1})
        blink_thread.start()
        beep_thread.start()
        blink_thread.join()
        beep_thread.join()

    @staticmethod
    def toggle_led(led, state):
        """Toggle a specific LED off/on.
        Takes 2 positional arguements:
        led : int - target LED-pin number (BCIM)
        state : bool - on/off, true is on """
        if state:
            GPIO.output(led, GPIO.HIGH)
        else:
            GPIO.output(led, GPIO.LOW)

    def clear_leds(self):
        """Turn both LEDS off, takes no arguments"""
        GPIO.output(self.led_green, GPIO.LOW)
        GPIO.output(self.led_red, GPIO.LOW)
