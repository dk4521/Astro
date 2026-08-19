"""The course, split one module per part.

Thirty chapters written out in full is a lot of prose, and prose is edited far
more often than the code around it. Keeping each part in its own module means a
correction to the nakshatra chapters never touches the file the dasha chapters
live in, and a reviewer reading a diff sees a part, not a wall.

Each module exports a `CHAPTERS` tuple in reading order. `content.py` chains
them; the order there is the order the reader walks, and the chapter numbers the
app displays are positions in that chain — so a chapter cannot be moved without
moving every cross-reference that names its number.
"""

from __future__ import annotations

# The six parts. Held here rather than in each module because the index screen
# groups by this string, and two spellings of "Foundations" would silently
# become two groups.
PART_FOUNDATIONS = {"en": "Foundations", "hi": "बुनियाद"}
PART_GRAHAS = {"en": "The grahas", "hi": "ग्रह"}
PART_HOUSES = {"en": "Houses", "hi": "भाव"}
PART_NAKSHATRAS = {"en": "Nakshatras", "hi": "नक्षत्र"}
PART_TIME = {"en": "Time", "hi": "काल"}
PART_PRACTICE = {"en": "Practice", "hi": "व्यवहार"}

__all__ = [
    "PART_FOUNDATIONS",
    "PART_GRAHAS",
    "PART_HOUSES",
    "PART_NAKSHATRAS",
    "PART_TIME",
    "PART_PRACTICE",
]
