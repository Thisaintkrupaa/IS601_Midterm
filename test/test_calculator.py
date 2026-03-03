import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory

from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory


@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"

            yield Calculator(config=config)


def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None


@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")


def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers


def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers


def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation


def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')


def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)


def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)


def test_perform_operation_modulus(calculator):
    calculator.set_operation(OperationFactory.create_operation('modulus'))
    result = calculator.perform_operation(10, 3)
    assert result == Decimal("1")


def test_perform_operation_int_divide(calculator):
    calculator.set_operation(OperationFactory.create_operation('int_divide'))
    result = calculator.perform_operation(10, 3)
    assert result == Decimal("3")


def test_perform_operation_percent(calculator):
    calculator.set_operation(OperationFactory.create_operation('percent'))
    result = calculator.perform_operation(1, 4)
    assert result == Decimal("25")


def test_perform_operation_abs_diff(calculator):
    calculator.set_operation(OperationFactory.create_operation('abs_diff'))
    result = calculator.perform_operation(2, 10)
    assert result == Decimal("8")


def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []


def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1


def test_undo_then_new_operation_clears_redo(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.perform_operation(5, 6)

    assert len(calculator.history) == 2

    assert calculator.undo() is True
    assert len(calculator.history) == 1

    assert calculator.redo() is True
    assert len(calculator.history) == 2

    assert calculator.undo() is True
    assert len(calculator.history) == 1

    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(2, 2)

    assert calculator.redo() is False


def test_notify_observers_called(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)

    with patch.object(observer, "update") as mock_update:
        calculator.set_operation(OperationFactory.create_operation('add'))
        calculator.perform_operation(2, 3)
        assert mock_update.called is True
        assert mock_update.call_count == 1


def test_autosave_observer_calls_save_history(calculator):
    with patch.object(calculator, "save_history") as mock_save:
        calculator.config.auto_save = True
        observer = AutoSaveObserver(calculator)
        calculator.add_observer(observer)

        calculator.set_operation(OperationFactory.create_operation('add'))
        calculator.perform_operation(2, 3)

        assert mock_save.called is True


@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()


@patch('app.calculator.pd.DataFrame.to_csv', side_effect=Exception("write failed"))
def test_save_history_failure_raises_operation_error(mock_to_csv, calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    with pytest.raises(OperationError, match="Failed to save history"):
        calculator.save_history()


@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })

    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")


@patch('app.calculator.pd.read_csv', side_effect=Exception("read failed"))
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history_failure_raises_operation_error(mock_exists, mock_read_csv, calculator):
    with pytest.raises(OperationError, match="Failed to load history"):
        calculator.load_history()


def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")


@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")


@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")