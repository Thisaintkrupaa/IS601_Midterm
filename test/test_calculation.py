import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError
import logging


def test_addition():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("5")


def test_subtraction():
    calc = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc.result == Decimal("2")


def test_multiplication():
    calc = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("2"))
    assert calc.result == Decimal("8")


def test_division():
    calc = Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")


def test_division_by_zero():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("0"))


def test_power():
    calc = Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("8")


def test_negative_power():
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("-3"))


def test_root():
    calc = Calculation(operation="Root", operand1=Decimal("16"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")


def test_invalid_root_negative_number():
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation(operation="Root", operand1=Decimal("-16"), operand2=Decimal("2"))


def test_invalid_root_zero_degree():
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation(operation="Root", operand1=Decimal("16"), operand2=Decimal("0"))


def test_modulus():
    calc = Calculation(operation="Modulus", operand1=Decimal("10"), operand2=Decimal("3"))
    assert calc.result == Decimal("1")


def test_modulus_by_zero():
    with pytest.raises(OperationError, match="Modulus by zero is not allowed"):
        Calculation(operation="Modulus", operand1=Decimal("10"), operand2=Decimal("0"))


def test_integer_division():
    calc = Calculation(operation="IntegerDivision", operand1=Decimal("10"), operand2=Decimal("3"))
    assert calc.result == Decimal("3")


def test_integer_division_by_zero():
    with pytest.raises(OperationError, match="Integer division by zero is not allowed"):
        Calculation(operation="IntegerDivision", operand1=Decimal("10"), operand2=Decimal("0"))


def test_percentage():
    calc = Calculation(operation="Percentage", operand1=Decimal("1"), operand2=Decimal("4"))
    assert calc.result == Decimal("25")


def test_percentage_by_zero():
    with pytest.raises(OperationError, match="Percentage division by zero is not allowed"):
        Calculation(operation="Percentage", operand1=Decimal("1"), operand2=Decimal("0"))


def test_absolute_difference():
    calc = Calculation(operation="AbsoluteDifference", operand1=Decimal("2"), operand2=Decimal("10"))
    assert calc.result == Decimal("8")


def test_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation(operation="Unknown", operand1=Decimal("5"), operand2=Decimal("3"))


def test_to_dict():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }


def test_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == "Addition"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")


def test_invalid_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


def test_format_result():
    calc = Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"


def test_equality():
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc1 == calc2
    assert calc1 != calc3


def test_from_dict_result_mismatch(caplog):
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "10",
        "timestamp": datetime.now().isoformat()
    }

    with caplog.at_level(logging.WARNING):
        Calculation.from_dict(data)

    assert "Loaded calculation result" in caplog.text
    assert "differs from computed result" in caplog.text

def test_repr():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    r = repr(calc)
    assert "Addition" in r
    assert "operand1=2" in r
    assert "result=5" in r



def test_str():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert str(calc) == "Addition(2, 3) = 5"