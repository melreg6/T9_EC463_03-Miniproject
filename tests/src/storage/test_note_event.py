import sys
import os
import unittest
from unittest.mock import MagicMock


sys.modules['machine'] = MagicMock()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.storage.note_event import NoteEvent


class TestNoteEvent(unittest.TestCase):
    """Test cases for NoteEvent class."""

    def test_init(self):
        """Test NoteEvent initialization."""
        event = NoteEvent(timestamp_ms=1000, pitch=60, magnitude=0.8, channel=1)
        self.assertEqual(event.timestamp_ms, 1000)
        self.assertEqual(event.pitch, 60)
        self.assertEqual(event.magnitude, 0.8)
        self.assertEqual(event.channel, 1)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        event = NoteEvent(timestamp_ms=2000, pitch=64, magnitude=0.5, channel=2)
        expected = {
            "timestamp_ms": 2000,
            "pitch": 64,
            "magnitude": 0.5,
            "channel": 2
        }
        self.assertEqual(event.to_dict(), expected)

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "timestamp_ms": 3000,
            "pitch": 67,
            "magnitude": 0.9,
            "channel": 3
        }
        event = NoteEvent.from_dict(data)
        self.assertEqual(event.timestamp_ms, 3000)
        self.assertEqual(event.pitch, 67)
        self.assertEqual(event.magnitude, 0.9)
        self.assertEqual(event.channel, 3)

if __name__ == '__main__':
    unittest.main()
