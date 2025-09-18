# main.py for Raspberry Pi Pico W
# Title: Pico Light Orchestra Instrument Code (with RGB LED Twinkle)

import machine
import time
import json
import asyncio
import math

# --- Pin Configuration ---
photo_sensor_pin = machine.ADC(28)          # light sensor
buzzer_pin       = machine.PWM(machine.Pin(16))  # buzzer

# RGB LED pins (PWM)
led_red   = machine.PWM(machine.Pin(12))
led_green = machine.PWM(machine.Pin(13))
led_blue  = machine.PWM(machine.Pin(14))

for led in (led_red, led_green, led_blue):
    led.freq(1000)   # smoother brightness changes

def stop_tone():
    buzzer_pin.duty_u16(0)
    buzzer_pin.deinit()
    for led in (led_red, led_green, led_blue):
        led.duty_u16(0)

# --- Wii-on-bright ---
TOP_PEAK_ADC = 40000
PEAK_MARGIN  = 120
REARM_BELOW  = 32000

BPM = 112
BEAT_SEC = 60.0 / BPM

WII_MELODY = [
    (74,0.5), (78,0.5), (85,0.5), (78,0.5), (78,0.5), (74,0.5),
    (74,0.5), (74,0.5), (73,0.5), (74,0.5), (78,0.5), (81,0.5),
    (85,0.5), (81,0.5), (78,0.5), (88,0.5), (87,0.5), (86,0.5),
]

_wii_playing = False
_wii_armed   = True
_wii_task    = None
_was_topbin  = False

C_MAJOR_MIDI = [
    48, 50, 52, 53, 55, 57, 59,
    60, 62, 64, 65, 67, 69, 71,
    72, 74, 76, 77, 79, 81, 83,
    84
]

def midi_to_freq(midi_note):
    return 440 * (2 ** ((midi_note - 69) / 12))

def lux_to_freq(x, theMin, theMax, use_log=True):
    if use_log:
        log_min = math.log(theMin)
        log_max = math.log(theMax)
        t = (math.log(max(x,1)) - log_min) / (log_max - log_min)
    else:
        t = (x - theMin) / (theMax - theMin)
    t = 1 - t
    t = max(0, min(1, t))
    idx = int(round(t * (len(C_MAJOR_MIDI) - 1)))
    midi_note = C_MAJOR_MIDI[idx]
    return midi_to_freq(midi_note)

# --- LED Helper Functions ---
def set_color(r, g, b):
    """Set LED color with 0–65535 values."""
    led_red.duty_u16(r)
    led_green.duty_u16(g)
    led_blue.duty_u16(b)

def twinkle_pattern(adc_val):
    """Map light/music intensity to a twinkling color pattern."""
    norm = min(max(adc_val, 0), 65535)
    # Cycle color bands based on ranges of light
    if norm < 20000:
        set_color(norm, 0, 65535 - norm)        # purple shift
    elif norm < 40000:
        set_color(0, norm, 65535 - norm // 2)   # teal shift
    else:
        set_color(65535 - norm, norm // 2, norm)  # warm shift

# --- Non-blocking Wii melody task ---
async def play_wii_melody_once():
    global _wii_playing
    _wii_playing = True
    for midi, beats in WII_MELODY:
        dur = max(1, beats) * BEAT_SEC
        if midi is None:
            buzzer_pin.duty_u16(0)
        else:
            buzzer_pin.freq(int(midi_to_freq(midi)))
            buzzer_pin.duty_u16(32768)
        # LEDs pulse while melody plays
        twinkle_pattern(machine.rng() & 0xFFFF)  # random sparkle
        await asyncio.sleep(dur)
    buzzer_pin.duty_u16(0)
    _wii_playing = False

# --- Main Loop ---
async def main():
    global _wii_playing, _wii_armed, _wii_task, _was_topbin
    min_light = 2000
    max_light = 40000

    while True:
        adc = photo_sensor_pin.read_u16()

        # LED twinkle always running
        twinkle_pattern(adc)

        # --- Wii trigger detection ---
        is_topbin = (adc >= (TOP_PEAK_ADC - PEAK_MARGIN))
        if _wii_armed and not _wii_playing and (not _was_topbin) and is_topbin:
            _wii_armed = False
            _wii_playing = True
            buzzer_pin.duty_u16(0)
            print(f"[Wii] Peak trigger at ADC={adc}")
            _wii_task = asyncio.create_task(play_wii_melody_once())

        if (not _wii_armed) and (not _wii_playing) and adc <= REARM_BELOW:
            _wii_armed = True
            print(f"[Wii] Re-armed (ADC={adc} ≤ {REARM_BELOW})")

        _was_topbin = is_topbin

        if not _wii_playing:
            frequency = lux_to_freq(adc, min_light, max_light)
            buzzer_pin.freq(int(frequency))
            buzzer_pin.duty_u16(32768)

        await asyncio.sleep(0.05)

# --- Run ---
if __name__ == "__main__":
    print("Pico Light Orchestra Starting…")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped.")
        stop_tone()
