"""Disclaimer, this countdown timer is intended for a pomodoro timer where
precision isn't all that important"""
import time

class CountDown:
    """Generic countdown timer class"""
    def __init__(self):
        self.paused = True
        self.start_time = 0
        self.duration = 0

    def set_duration(self, duration):
        self.duration = duration

    def start(self):
        self.start_time = time.time()
        self.paused = False

    def pause(self):
        self.duration -= (time.time() - self.start_time)
        self.paused = True

    def check_expired(self):
        if not self.paused:
            if time.time() >= self.start_time + self.duration:
                return True
            else:
                return False
        else:
            return False

    def get_remaining_string(self):
        if not self.paused:
            elapsed = time.time() - self.start_time
        else:
            elapsed = 0
    
        remaining = self.duration - elapsed
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        s = (remaining % 3600) % 60
        return "{:02}:{:02}:{:02}".format(int(hrs), int(mins), int(s))
