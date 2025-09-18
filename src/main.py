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
TOP_PEAK_ADC = 40000       # observed max
PEAK_MARGIN  = 120         # accept >= (max - margin) as "brightest"
REARM_BELOW  = 32000       # must fall below this to re-arm

BPM = 112
BEAT_SEC = 60.0 / BPM

# Opening phrase of the Mii Channel theme (lead line)
# (MIDI note or None for rest, beats)
WII_MELODY = [
    (74,0.5),  # D5
    (78,0.5),  # F#5
    (85,0.5),  # C#6
    (78,0.5),  # F#5
    (78,0.5),  # F#5
    (74,0.5),  # D5
    (74,0.5),  # D5
    (74,0.5),  # D5
    (73,0.5),  # C#5
    (74,0.5),  # D5
    (78,0.5),  # F#5
    (81,0.5),  # A5
    (85,0.5),  # C#6
    (81,0.5),  # A5
    (78,0.5),  # F#5
    (88,0.5),  # E6
    (87,0.5),  # D#6
    (86,0.5),  # D6
]

# one-shot control
_wii_playing = False   # True while the one-shot melody is running
_wii_armed   = True    # re-armed after brightness falls below REARM_BELOW
_wii_task    = None
_was_topbin  = False   # rising-edge detector for the top bin


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
            adc = photo_sensor_pin.read_u16()

            # --- Peak bin detection (rising edge only) ---
            is_topbin = (adc >= (TOP_PEAK_ADC - PEAK_MARGIN))

            # Trigger ONCE when we ENTER the top bin (rising edge)
            if _wii_armed and not _wii_playing and (not _was_topbin) and is_topbin:
                _wii_armed = False          # disarm until we drop below REARM_BELOW
                _wii_playing = True         # claim the buzzer immediately
                buzzer_pin.duty_u16(0)      # hard mute any scale tone
                print(f"[Wii] Peak trigger at ADC={adc} (≥ {TOP_PEAK_ADC - PEAK_MARGIN})")
                _wii_task = asyncio.create_task(play_wii_melody_once())

            # Re-arm ONLY after we leave bright territory by enough margin
            if (not _wii_armed) and (not _wii_playing) and adc <= REARM_BELOW:
                _wii_armed = True
                print(f"[Wii] Re-armed (ADC={adc} ≤ {REARM_BELOW})")

            # Update edge detector
            _was_topbin = is_topbin

            # While the melody plays, DO NOT play the C-major scale
            if not _wii_playing:
                frequency = lux_to_freq(adc, min_light, max_light)
                buzzer_pin.freq(int(frequency))
                buzzer_pin.duty_u16(32768)
                # print(f"[Scale] ADC={adc} -> {int(frequency)} Hz")

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
