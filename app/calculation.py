########################
# Calculation Model     #
########################

from __future__ import annotations

from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict

from app.exceptions import OperationError


@dataclass
class Calculation:
    """Represents a single calculation record."""

    operation: str
    operand1: Decimal
    operand2: Decimal

    result: Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self) -> None:
        self.result = self.calculate()

    def calculate(self) -> Decimal:
        ops = {
            "Addition": lambda x, y: x + y,
            "Subtraction": lambda x, y: x - y,
            "Multiplication": lambda x, y: x * y,
            "Division": lambda x, y: x / y if y != 0 else self._raise_div_zero(),
            "Power": lambda x, y: Decimal(pow(float(x), float(y))) if y >= 0 else self._raise_neg_power(),
            "Root": lambda x, y: (
                Decimal(pow(float(x), 1 / float(y)))
                if x >= 0 and y != 0
                else self._raise_invalid_root(x, y)
            ),
            # ✅ Required additional operations
            "Modulus": lambda x, y: x % y if y != 0 else self._raise_mod_zero(),
            "IntegerDivision": lambda x, y: x // y if y != 0 else self._raise_int_div_zero(),
            "Percentage": lambda x, y: (x / y) * Decimal("100") if y != 0 else self._raise_percent_zero(),
            "AbsoluteDifference": lambda x, y: abs(x - y),
        }

        op = ops.get(self.operation)
        if not op:
            raise OperationError(f"Unknown operation: {self.operation}")

        try:
            return op(self.operand1, self.operand2)
        except (InvalidOperation, ValueError, ArithmeticError) as e:  # pragma: no cover
            raise OperationError(f"Calculation failed: {e}")

    @staticmethod
    def _raise_div_zero() -> Decimal:  # pragma: no cover
        raise OperationError("Division by zero is not allowed")

    @staticmethod
    def _raise_mod_zero() -> Decimal:  # pragma: no cover
        raise OperationError("Modulus by zero is not allowed")

    @staticmethod
    def _raise_int_div_zero() -> Decimal:  # pragma: no cover
        raise OperationError("Integer division by zero is not allowed")

    @staticmethod
    def _raise_percent_zero() -> Decimal:  # pragma: no cover
        raise OperationError("Percentage division by zero is not allowed")

    @staticmethod
    def _raise_neg_power() -> Decimal:  # pragma: no cover
        raise OperationError("Negative exponents are not supported")

    @staticmethod
    def _raise_invalid_root(x: Decimal, y: Decimal) -> Decimal:  # pragma: no cover
        if y == 0:
            raise OperationError("Zero root is undefined")
        if x < 0:
            raise OperationError("Cannot calculate root of negative number")
        raise OperationError("Invalid root operation")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Calculation":
        try:
            calc = Calculation(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"]),
            )
            calc.timestamp = datetime.datetime.fromisoformat(data["timestamp"])

            saved_result = Decimal(data["result"])
            if calc.result != saved_result:
                logging.warning(
                    "Loaded calculation result %s differs from computed result %s",
                    saved_result, calc.result
                )  # pragma: no cover

            return calc

        except (KeyError, InvalidOperation, ValueError) as e:  # pragma: no cover
            raise OperationError(f"Invalid calculation data: {e}")

    def __str__(self) -> str:
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:
        return (
            f"Calculation(operation='{self.operation}', "
            f"operand1={self.operand1}, operand2={self.operand2}, "
            f"result={self.result}, timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):  # pragma: no cover
            return NotImplemented
        return (
            self.operation == other.operation
            and self.operand1 == other.operand1
            and self.operand2 == other.operand2
            and self.result == other.result
        )

    def format_result(self, precision: int = 10) -> str:
        try:
            return str(
                self.result.normalize()
                .quantize(Decimal("0." + "0" * precision))
                .normalize()
            )
        except InvalidOperation:  # pragma: no cover
            return str(self.result)