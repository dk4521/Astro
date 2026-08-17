"""The interpretation layer.

The AI translates the engine's output into language. It never computes any part
of a chart, and `grounding` checks each answer against the chart it claims to
describe — so a fabricated placement is detectable rather than merely
discouraged.
"""

from .client import InterpretationUnavailable, is_configured, set_client
from .facts import build_brief
from .interpret import Interpretation, Turn, answer, reading, stream_answer

__all__ = [
    "Interpretation",
    "InterpretationUnavailable",
    "Turn",
    "answer",
    "build_brief",
    "is_configured",
    "reading",
    "set_client",
    "stream_answer",
]
