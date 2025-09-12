from machine import ADC, Pin

class ADCReader:
    def __init__(self, pin, alpha=0.2):
        """
        pin: GPIO pin number connected to the LDR voltage divider
        alpha: smoothing factor for EMA filter (0 < alpha <= 1)
        """
        self.adc = ADC(Pin(pin))
        self.alpha = alpha
        self.filtered = 0.0

    def read_raw(self):
        """Return raw ADC value (0–65535)."""
        return self.adc.read_u16()

    def read_norm(self):
        """
        Return normalized + smoothed value (0.0–1.0).
        Uses exponential moving average for noise reduction.
        """
        raw = self.read_raw() / 65535.0
        self.filtered = (1 - self.alpha) * self.filtered + self.alpha * raw
        return self.filtered
