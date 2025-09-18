# main.py for Raspberry Pi Pico W
# Title: Pico Light Orchestra Instrument Code
     
import machine
import time
import json
import asyncio
import math

# --- Pin Configuration ---
photo_sensor_pin = machine.ADC(28)                  # photosensor on GP28 (ADC2)
buzzer_pin = machine.PWM(machine.Pin(16))           # buzzer on GP16 (PWM)

def stop_tone():
    buzzer_pin.duty_u16(0)
    buzzer_pin.deinit()

# --- Wii-on-bright (PEAK TRIGGER: one-shot, for INVERTED sensor) ---
# Bright = LOW ADC. Trigger once when we ENTER the lowest bin near your bright minimum.
LOW_PEAK_ADC = 2000        # your "brightest" typical reading (tune this)
PEAK_MARGIN  = 200         # accept <= (LOW_PEAK_ADC + margin) as "brightest"
REARM_ABOVE  = 6000        # must rise above this (dimmer) to re-arm

BPM = 112
BEAT_SEC = 60.0 / BPM

# Wii melody (MIDI, beats)
WII_MELODY = [
    (74,0.5),(78,0.5),(85,0.5),(78,0.5),(78,0.5),
    (74,0.5),(74,0.5),(74,0.5),(73,0.5),(74,0.5),
    (78,0.5),(81,0.5),(85,0.5),(81,0.5),(78,0.5),
    (88,0.5),(87,0.5),(86,0.5),
]

# one-shot control
_wii_playing = False
_wii_armed   = True
_wii_task    = None
_was_lowbin  = False   # edge detector for the LOW (bright) bin

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
        t = (math.log(x) - log_min) / (log_max - log_min)
    else:
        t = (x - theMin) / (theMax - theMin)
    t = 1 - t
    t = max(0, min(1, t))
    idx = int(round(t * (len(C_MAJOR_MIDI) - 1)))
    midi_note = C_MAJOR_MIDI[idx]
    return midi_to_freq(midi_note)

# --- One-shot Wii melody task ---
async def play_wii_melody_once():
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
    buzzer_pin.duty_u16(0)
    _wii_playing = False

async def main():
    global _wii_playing, _wii_armed, _wii_task, _was_lowbin

    # scale mapping range (tune if needed)
    min_light = 2000
    max_light = 40000

    while True:
        try:
            adc = photo_sensor_pin.read_u16()

            # --- LOW bin (bright) detection with rising-edge logic ---
            is_lowbin = (adc <= (LOW_PEAK_ADC + PEAK_MARGIN))

            # Trigger ONCE when we ENTER the low bin (i.e., go bright enough)
            if _wii_armed and not _wii_playing and (not _was_lowbin) and is_lowbin:
                _wii_armed = False
                _wii_playing = True
                buzzer_pin.duty_u16(0)      # mute scale immediately
                print(f"[Wii] Peak BRIGHT trigger at ADC={adc} (≤ {LOW_PEAK_ADC + PEAK_MARGIN})")
                _wii_task = asyncio.create_task(play_wii_melody_once())

            # Re-arm ONLY after we get clearly dimmer again
            if (not _wii_armed) and (not _wii_playing) and adc >= REARM_ABOVE:
                _wii_armed = True
                print(f"[Wii] Re-armed (ADC={adc} ≥ {REARM_ABOVE})")

            # update edge detector
            _was_lowbin = is_lowbin

            # While melody plays, DO NOT play the C-major scale
            if not _wii_playing:
                frequency = lux_to_freq(adc, min_light, max_light)
                buzzer_pin.freq(int(frequency))
                buzzer_pin.duty_u16(32768)

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


