# main.py for Raspberry Pi Pico W
# Title: Pico Light Orchestra Instrument Code

import machine
import time
import json
import asyncio
import math

# --- Pin Configuration ---
# The photosensor is connected to an Analog-to-Digital Converter (ADC) pin.
# We will read the voltage, which changes based on light.
photo_sensor_pin = machine.ADC(28)

# The buzzer is connected to a GPIO pin that supports Pulse Width Modulation (PWM).
# PWM allows us to create a square wave at a specific frequency to make a sound.
buzzer_pin = machine.PWM(machine.Pin(16))

def stop_tone():
    buzzer_pin.duty_u16(0)   # duty cycle = 0% (silent)
    buzzer_pin.deinit()      # release the PWM hardware

C_MAJOR_MIDI = [
    48, 50, 52, 53, 55, 57, 59,   # C3..B3
    60, 62, 64, 65, 67, 69, 71,   # C4..B4
    72, 74, 76, 77, 79, 81, 83,   # C5..B5
    84                            # C6
]

def midi_to_freq(midi_note):
    return 440 * (2 ** ((midi_note - 69) / 12))

def lux_to_freq(x,theMin, theMax, use_log=True):
    if use_log:
        # log scale, inverted
        log_min = math.log(theMin)
        log_max = math.log(theMax)
        t = (math.log(x) - log_min) / (log_max - log_min)
    else:
        # linear scale, inverted
        t = (x - theMin) / (theMax - theMin)
    
    # invert
    t = 1 - t  
    t = max(0, min(1, t))
    
    idx = int(round(t * (len(C_MAJOR_MIDI) - 1)))
    midi_note = C_MAJOR_MIDI[idx]
    return midi_to_freq(midi_note)

async def main():
    """Main execution loop."""

    # This loop runs the "default" behavior: playing sound based on light
    while True:
        try:
            light_value = photo_sensor_pin.read_u16()
            min_light = 2000
            max_light = 40000

            frequency = lux_to_freq(light_value, min_light, max_light)
            print(f"Playing a note at {frequency}")
            buzzer_pin.freq(int(frequency))
            buzzer_pin.duty_u16(32768)

            await asyncio.sleep(0.1)  # let event loop breathe

        except KeyboardInterrupt:
            print("Stopping main loop...")
            stop_tone()
            break

# Run the main event loop
if __name__ == "__main__":

    print("Hello World!")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped.")
        stop_tone()
