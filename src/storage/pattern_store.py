import json
import os
from typing import List, Dict, Tuple
from .note_event import NoteEvent


class PatternStore:
    """
    Manages saving, loading, and listing patterns.
    Each pattern is stored as a JSON file with metadata and events.
    """

    def __init__(self, base_path: str = "/patterns"):
        self.base_path = base_path
        try:
            os.mkdir(self.base_path)
        except OSError:
            pass

    def save(self, name: str, metadata: Dict, events: List[NoteEvent]):
        """Save a pattern to storage."""

        file_path = f"{self.base_path}/{name}.json"
        data = {
            "metadata": metadata,
            "events": [e.to_dict() for e in events]
        }

        with open(file_path, "w") as f:
            json.dump(data, f)

    def load(self, name: str) -> Tuple[Dict, List[NoteEvent]]:
        """Load a pattern from storage."""

        file_path = f"{self.base_path}/{name}.json"
        with open(file_path, "r") as f:
            data = json.load(f)
        metadata = data.get("metadata", {})
        events = [NoteEvent.from_dict(e) for e in data.get("events", [])]

        return metadata, events

    def list_patterns(self) -> List[str]:
        """List all saved patterns."""

        return [f[:-5] for f in os.listdir(self.base_path) if f.endswith(".json")]

    def delete(self, pattern_name: str):
        """Delete a pattern given a pattern name."""

        file_path = f"{self.base_path}/{pattern_name}.json"
        os.remove(file_path)

    def exists(self, pattern_name: str) -> bool:
        """Check if a pattern exists given a pattern name."""

        file_path = f"{self.base_path}/{pattern_name}.json"
        return os.path.exists(file_path)
