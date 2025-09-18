from typing import Dict


class NoteEvent:
    def __init__(self, timestamp_ms: int, pitch: int, magnitude: float, channel: int = 0):
        self.timestamp_ms = timestamp_ms
        self.pitch = pitch
        self.magnitude = magnitude
        self.channel = channel

    def to_dict(self) -> Dict:
        return {
            "timestamp_ms": self.timestamp_ms,
            "pitch": self.pitch,
            "magnitude": self.magnitude,
            "channel": self.channel
        }

    @staticmethod
    def from_dict(d: Dict) -> 'NoteEvent':
        return NoteEvent(d['timestamp_ms'], d['pitch'], d['magnitude'], d.get('channel', 0))
