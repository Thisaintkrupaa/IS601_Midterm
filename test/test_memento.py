from decimal import Decimal
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation


def test_memento_to_dict_and_from_dict():
    history = [
        Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    ]
    m = CalculatorMemento(history=history)

    d = m.to_dict()
    m2 = CalculatorMemento.from_dict(d)

    assert len(m2.history) == 1
    assert m2.history[0].operation == "Addition"
    assert m2.history[0].operand1 == Decimal("2")
    assert m2.history[0].operand2 == Decimal("3")