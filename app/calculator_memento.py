########################
# Calculator Memento   #
########################

from __future__ import annotations

from dataclasses import dataclass, field
import datetime as dt
from typing import Any, Dict, List

from app.calculation import Calculation
from app.exceptions import OperationError


@dataclass(frozen=True)
class CalculatorMemento:
    """Snapshot of calculator history for undo/redo."""

    history: List[Calculation]
    timestamp: dt.datetime = field(default_factory=dt.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "history": [c.to_dict() for c in self.history],
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CalculatorMemento":
        try:
            history_data = data["history"]
            timestamp_str = data["timestamp"]

            history = [Calculation.from_dict(item) for item in history_data]
            timestamp = dt.datetime.fromisoformat(timestamp_str)

            return cls(history=history, timestamp=timestamp)

        except (KeyError, TypeError, ValueError) as e:  # pragma: no cover
            raise OperationError(f"Invalid memento data: {e}")