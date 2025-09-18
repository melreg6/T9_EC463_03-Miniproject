import sys
import os
import unittest
from unittest.mock import MagicMock


sys.modules['machine'] = MagicMock()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src import midi_to_freq, lux_to_freq

class TestMainFunctions(unittest.TestCase):
    """Test cases for main.py functions."""

    def test_midi_to_freq(self):
        """Test MIDI note to frequency conversion."""
        self.assertAlmostEqual(midi_to_freq(69), 440.0, places=2)
        self.assertAlmostEqual(midi_to_freq(60), 261.63, places=2)
        self.assertAlmostEqual(midi_to_freq(48), 130.81, places=2)

    def test_lux_to_freq_log_scale(self):
        """Test lux to frequency conversion with log scale."""
        min_light = 2000
        max_light = 40000

        # At min light, should get highest note (C6, MIDI 84)
        freq_min = lux_to_freq(min_light, min_light, max_light, use_log=True)
        expected_min = midi_to_freq(84)
        self.assertAlmostEqual(freq_min, expected_min, delta=1.0)

        # At max light, should get lowest note (C3, MIDI 48)
        freq_max = lux_to_freq(max_light, min_light, max_light, use_log=True)
        expected_max = midi_to_freq(48)
        self.assertAlmostEqual(freq_max, expected_max, delta=1.0)

        # At midpoint, should be around C4 (MIDI 60)
        mid_light = (min_light + max_light) / 2
        freq_mid = lux_to_freq(mid_light, min_light, max_light, use_log=True)
        expected_mid = midi_to_freq(60)
        self.assertAlmostEqual(freq_mid, expected_mid, delta=50.0)  # Allow larger tolerance

    def test_lux_to_freq_linear_scale(self):
        """Test lux to frequency conversion with linear scale."""
        min_light = 2000
        max_light = 40000

        # At min light, should get highest note
        freq_min = lux_to_freq(min_light, min_light, max_light, use_log=False)
        expected_min = midi_to_freq(84)
        self.assertAlmostEqual(freq_min, expected_min, delta=1.0)

        # At max light, should get lowest note
        freq_max = lux_to_freq(max_light, min_light, max_light, use_log=False)
        expected_max = midi_to_freq(48)
        self.assertAlmostEqual(freq_max, expected_max, delta=1.0)

    def test_lux_to_freq_edge_cases(self):
        """Test edge cases for lux_to_freq."""
        min_light = 1000
        max_light = 50000

        # Test with value below min
        freq_below = lux_to_freq(500, min_light, max_light)
        expected_max = midi_to_freq(84)  # Should clamp to max (highest note)
        self.assertAlmostEqual(freq_below, expected_max, delta=1.0)

        # Test with value above max
        freq_above = lux_to_freq(60000, min_light, max_light)
        expected_min = midi_to_freq(48)  # Should clamp to min (lowest note)
        self.assertAlmostEqual(freq_above, expected_min, delta=1.0)

if __name__ == '__main__':
    unittest.main()
