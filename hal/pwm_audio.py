from machine import Pin, PWM
import time

class PWMAudio:
    def __init__(self, pin=15):
        """
        pin: GPIO pin number for buzzer
        """
        self.pwm = PWM(Pin(pin))
        self.pwm.duty_u16(0)  # start off

    def play_tone(self, freq_hz, duration_ms, volume=0.5):
        """
        Play a tone at frequency freq_hz for duration_ms milliseconds.
        volume: 0.0–1.0 (duty cycle)
        """
        self.pwm.freq(int(freq_hz))
        duty = int(volume * 32767)  # half of max duty
        self.pwm.duty_u16(duty)
        time.sleep_ms(duration_ms)
        self.stop()

    def stop(self):
        """Turn off the buzzer."""
        self.pwm.duty_u16(0)
