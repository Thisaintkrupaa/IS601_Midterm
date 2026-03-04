########################
# Input Validation     #
########################

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError


@dataclass
class InputValidator:

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        try:
            if isinstance(value, str):
                value = value.strip()

            if value is None or (isinstance(value, str) and value == ""):
                raise ValidationError(f"Invalid number format: {value}")

            if not isinstance(value, (int, float, Decimal, str)):
                raise ValidationError(f"Invalid number format: {value}")

            number = Decimal(str(value))

            if number.is_nan() or number.is_infinite():  # pragma: no cover
                raise ValidationError(f"Invalid number format: {value}")

            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")

            return number.normalize()

        except ValidationError:
            raise
        except InvalidOperation:
            raise ValidationError(f"Invalid number format: {value}")