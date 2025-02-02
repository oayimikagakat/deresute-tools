from enum import Enum


class NoteType(Enum):
    TAP = 0
    LONG = 1
    FLICK = 2
    SLIDE = 3
    DAMAGE = -1

    def __str__(self):
        return self.name
