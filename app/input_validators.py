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
    """Validates and sanitizes calculator inputs."""

    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        try:
            if value is None:
                raise ValidationError("Input cannot be None")

            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    raise ValidationError("Input cannot be empty")

            number = Decimal(str(value))

            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")

            return number.normalize()

        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e