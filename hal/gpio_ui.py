from machine import Pin

class UI:
    def __init__(self, button_pins, led_pins):
        """
        button_pins: dict {id: GPIO pin}
        led_pins: dict {id: GPIO pin}
        """
        self.buttons = {
            bid: Pin(pin, Pin.IN, Pin.PULL_DOWN) for bid, pin in button_pins.items()
        }
        self.leds = {
            lid: Pin(pin, Pin.OUT) for lid, pin in led_pins.items()
        }

    def button_pressed(self, btn_id):
        """Return True if button is pressed."""
        return self.buttons[btn_id].value()

    def led_set(self, led_id, on):
        """Control LED (common cathode → HIGH=ON)."""
        self.leds[led_id].value(1 if on else 0)
