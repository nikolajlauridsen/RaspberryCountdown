"""Various time related functions used in calculating statistics"""


def get_duration_sum(session_data):
    summation = 0

    for session in session_data:
        summation += session["duration"]
    return summation


def seconds_to_timestamp(seconds):
    """Convert seconds into a neatly formatted string.
    Format: HH:MM:SS
    Returns: Timestamp string."""
    hrs = seconds //3600
    mins = (seconds % 3600) // 60
    s = (seconds % 3600) % 60
    return "{:02}:{:02}:{:02}".format(int(hrs), int(mins), int(s))
