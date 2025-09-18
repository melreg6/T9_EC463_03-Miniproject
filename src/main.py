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

# --- Wii-on-bright ---
BRIGHT_ON  = 52000   # start melody when reading crosses above this
BRIGHT_OFF = 50000   # re-arm when reading falls below this (hysteresis)

BPM = 112
BEAT_SEC = 60.0 / BPM

# Opening phrase of the Mii Channel theme (lead line)
# (MIDI note or None for rest, beats)
WII_MELODY = [
    (81,0.5),(81,0.5),(78,0.5),(78,0.5),(74,0.5),(74,0.5),(76,0.5),(78,1.0),
    (73,0.5),(74,0.5),(76,0.5),(78,0.5),(81,1.0),(None,0.5),
    (80,0.5),(81,0.5),(85,1.0),(88,1.5),(87,0.5),(86,0.5),(85,0.5),
]

# one-shot control
_wii_playing = False   # True while the one-shot melody is running
_wii_armed   = True    # re-armed after brightness falls below BRIGHT_OFF
_wii_task    = None


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

# --- Non-blocking Wii melody task (NEW) ---
async def play_wii_melody_once():
    """Play the Wii phrase exactly once, then release the buzzer."""
    global _wii_playing
    _wii_playing = True
    for midi, beats in WII_MELODY:
        dur = max(1, beats) * BEAT_SEC
        if midi is None:
            buzzer_pin.duty_u16(0)
        else:
            buzzer_pin.freq(int(midi_to_freq(midi)))
            buzzer_pin.duty_u16(32768)  # 50% duty
        await asyncio.sleep(dur)
    buzzer_pin.duty_u16(0)     # ensure silence at the end
    _wii_playing = False


async def main():
    """Main execution loop."""
    global _wii_playing, _wii_armed, _wii_task

    # scale mapping range (tune to your room)
    min_light = 2000
    max_light = 40000

    while True:
        try:
            light_value = photo_sensor_pin.read_u16()

            # start the melody ONCE
            if _wii_armed and not _wii_playing and light_value >= BRIGHT_ON:
                _wii_armed = False          # disarm until brightness falls
                _wii_playing = True         # claim the buzzer immediately
                buzzer_pin.duty_u16(0)      # hard mute any scale tone
                print(f"[Wii] Triggered (ADC={light_value}) → one-shot melody")
                _wii_task = asyncio.create_task(play_wii_melody_once())

            # Re-arm ONLY after brightness drops below BRIGHT_OFF
            if not _wii_armed and not _wii_playing and light_value <= BRIGHT_OFF:
                _wii_armed = True
                print(f"[Wii] Re-armed (ADC={light_value})")
            # ------------------------------------------------------

            # While the melody plays, DO NOT play the C-major scale
            if not _wii_playing:
                frequency = lux_to_freq(light_value, min_light, max_light)
                buzzer_pin.freq(int(frequency))
                buzzer_pin.duty_u16(32768)
                # print(f"[Scale] ADC={light_value} -> {int(frequency)} Hz")

            await asyncio.sleep(0.05)

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
