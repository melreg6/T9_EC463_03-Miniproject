import sys
import os
import tempfile
import unittest
import shutil
from unittest.mock import MagicMock


sys.modules['machine'] = MagicMock()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.storage.note_event import NoteEvent
from src.storage.pattern_store import PatternStore


class TestPatternStore(unittest.TestCase):
    """Test cases for PatternStore class."""

    def setUp(self):
        """Set up temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.store = PatternStore(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir)

    def test_init_creates_directory(self):
        """Test that PatternStore creates the base directory."""
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.isdir(self.temp_dir))

    def test_save_and_load(self):
        """Test saving and loading a pattern."""
        metadata = {"name": "Test Pattern", "tempo": 120}
        events = [
            NoteEvent(0, 60, 0.8),
            NoteEvent(500, 64, 0.6),
            NoteEvent(1000, 67, 0.9)
        ]

        self.store.save("test_pattern", metadata, events)
        loaded_metadata, loaded_events = self.store.load("test_pattern")

        self.assertEqual(loaded_metadata, metadata)
        self.assertEqual(len(loaded_events), 3)
        self.assertEqual(loaded_events[0].timestamp_ms, 0)
        self.assertEqual(loaded_events[0].pitch, 60)
        self.assertEqual(loaded_events[1].timestamp_ms, 500)
        self.assertEqual(loaded_events[1].pitch, 64)

    def test_list_patterns(self):
        """Test listing saved patterns."""

        self.assertEqual(self.store.list_patterns(), [])

        self.store.save("pattern1", {}, [])
        self.store.save("pattern2", {}, [])
        self.store.save("pattern3", {}, [])

        patterns = self.store.list_patterns()
        self.assertEqual(len(patterns), 3)
        self.assertIn("pattern1", patterns)
        self.assertIn("pattern2", patterns)
        self.assertIn("pattern3", patterns)

    def test_delete_pattern(self):
        """Test deleting a pattern."""
        self.store.save("to_delete", {}, [])
        self.assertTrue(self.store.exists("to_delete"))

        self.store.delete("to_delete")
        self.assertFalse(self.store.exists("to_delete"))
        self.assertNotIn("to_delete", self.store.list_patterns())

    def test_exists(self):
        """Test checking if a pattern exists."""
        self.assertFalse(self.store.exists("nonexistent"))

        self.store.save("existing", {}, [])
        self.assertTrue(self.store.exists("existing"))

    def test_load_nonexistent_pattern(self):
        """Test loading a nonexistent pattern raises error."""
        with self.assertRaises(OSError):  # FileNotFoundError in MicroPython might be OSError
            self.store.load("nonexistent")

    def test_delete_nonexistent_pattern(self):
        """Test deleting a nonexistent pattern raises error."""
        with self.assertRaises(OSError):
            self.store.delete("nonexistent")

    def test_save_overwrites_existing(self):
        """Test that saving overwrites existing pattern."""

        self.store.save("overwrite_test", {"version": 1}, [NoteEvent(0, 60, 1.0)])

        self.store.save("overwrite_test", {"version": 2}, [NoteEvent(0, 72, 0.5)])

        metadata, events = self.store.load("overwrite_test")
        self.assertEqual(metadata["version"], 2)
        self.assertEqual(events[0].pitch, 72)

if __name__ == '__main__':
    unittest.main()
