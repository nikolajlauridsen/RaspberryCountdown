"""Disclaimer, this countdown timer is intended for a pomodoro timer where
precision isn't all that important

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
import time

class CountDown:
    """Generic countdown timer class"""
    def __init__(self):
        self.paused = True
        self.start_time = 0
        self.duration = 0

    def set_duration(self, duration):
        """Set (or reset) the duration of the countdown clock."""
        self.duration = duration

    def start(self):
        """Start/Resume the clock.
        Sets pause flag to false."""
        self.start_time = time.time()
        self.paused = False

    def pause(self):
        """Pause the countdown clock.
        Reduces duration with time elapsed.
        Sets pause flag to true."""
        self.duration -= (time.time() - self.start_time)
        self.paused = True

    def check_expired(self):
        """Check whether the countdown timer has expired.
        Returns: True/False"""
        if not self.paused:
            if time.time() >= self.start_time + self.duration:
                return True
            else:
                return False
        else:
            return False

    def get_remaining_string(self):
        """Get the remaining time as a string representation.
        Format: HH:MM:SS
        Returns: Remaining time as a string."""
        if not self.paused:
            elapsed = time.time() - self.start_time
        else:
            elapsed = 0

        remaining = self.duration - elapsed
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        s = (remaining % 3600) % 60
        return "{:02}:{:02}:{:02}".format(int(hrs), int(mins), int(s))

    @staticmethod
    def seconds_to_timestamp(seconds):
        """Convert seconds into a neatly formatted string.
        Format: HH:MM:SS
        Returns: Timestamp string."""
        hrs = seconds //3600
        mins = (seconds % 3600) // 60
        s = (seconds % 3600) % 60
        return "{:02}:{:02}:{:02}".format(int(hrs), int(mins), int(s))
