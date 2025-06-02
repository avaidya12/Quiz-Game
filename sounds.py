# sounds.py
import winsound
import time

def play_correct_sound():
    """Plays a sound for correct answer"""
    frequency = 2500  # Hz, waves per second
    duration = 1000   # ms, duration of sound
    winsound.Beep(frequency, duration)

def play_wrong_sound():
    """Plays a sound for wrong answer"""
    frequency = 1000  # Hz, waves per second
    duration = 1000   # ms, duration of sound
    winsound.Beep(frequency, duration)

def play_welcome_sound():
    frequency = 1000  # Hz
    duration = 200    # milliseconds
    winsound.Beep(frequency, duration)
    winsound.Beep(int(frequency * 1.5), duration)
    winsound.Beep(frequency, duration)
    