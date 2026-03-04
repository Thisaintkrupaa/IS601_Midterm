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
from app.history import LoggingObserver
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
    calculator.set_operation(OperationFactory.create_operation('add'))
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
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    assert calculator.undo() is True
    assert calculator.history == []


def test_redo(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.redo() is True
    assert len(calculator.history) == 1


def test_undo_then_new_operation_clears_redo(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.perform_operation(5, 6)

    assert len(calculator.history) == 2

    assert calculator.undo() is True
    assert len(calculator.history) == 1

    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(2, 2)

    assert calculator.redo() is False


@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()


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

    calculator.load_history()
    assert len(calculator.history) == 1
    assert calculator.history[0].operation == "Addition"
    assert calculator.history[0].operand1 == Decimal("2")
    assert calculator.history[0].operand2 == Decimal("3")
    assert calculator.history[0].result == Decimal("5")


def test_clear_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


def _printed_text(mock_print):
    return "\n".join(str(call.args[0]) for call in mock_print.call_args_list if call.args)


@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        out = _printed_text(mock_print)
        assert "Goodbye!" in out


@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Available commands:" in out
    assert "stats - Show statistics about calculations" in out


@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "2 + 3 = 5" in out


@patch('builtins.input', side_effect=['stats', 'exit'])
@patch('builtins.print')
def test_calculator_repl_stats_no_history(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "No calculations yet." in out


@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_nothing(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Nothing to undo" in out


@patch('builtins.input', side_effect=['add', '2', '3', 'undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Operation undone" in out


@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_nothing(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Nothing to redo" in out


@patch('builtins.input', side_effect=['add', '2', '3', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Operation redone" in out


@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history_empty(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "No calculations in history" in out


@patch('builtins.input', side_effect=['add', '2', '3', 'history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history_with_entries(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Calculation History:" in out


@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "History cleared" in out


@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "History saved successfully" in out


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "History loaded successfully" in out


@patch('builtins.input', side_effect=['unknown_cmd', 'exit'])
@patch('builtins.print')
def test_calculator_repl_unknown_command(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Unknown command" in out


@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_first_number(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Operation cancelled" in out


@patch('builtins.input', side_effect=['add', '2', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_second_number(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Operation cancelled" in out


@patch('builtins.input', side_effect=['add', 'abc', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_invalid_number(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Error" in out


@patch('builtins.input', side_effect=['divide', '1', '0', 'exit'])
@patch('builtins.print')
def test_calculator_repl_division_by_zero(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Error" in out


@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_save_fails_on_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history', side_effect=Exception("disk full")), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Goodbye!" in out


@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save_error(mock_print, mock_input):
    call_count = 0
    def save_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("disk error")
    with patch('app.calculator.Calculator.save_history', side_effect=save_side_effect), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Error saving history" in out


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load_error(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history', side_effect=Exception("file error")), \
         patch('app.calculator.Calculator.save_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Error loading history" in out


@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_calculator_repl_eof(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Input terminated" in out


@patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit'])
@patch('builtins.print')
def test_calculator_repl_keyboard_interrupt(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Operation cancelled" in out


@patch('builtins.input', side_effect=['', 'exit'])
@patch('builtins.print')
def test_calculator_repl_empty_command(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Goodbye!" in out


@patch('builtins.input', side_effect=['add', '2', '3', 'stats', 'exit'])
@patch('builtins.print')
def test_calculator_repl_stats_with_history(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history'), \
         patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    out = _printed_text(mock_print)
    assert "Calculator Statistics" in out


# --- calculator.py branch coverage ---

def test_calculator_init_load_history_warning(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    with patch('app.calculator.Calculator.load_history', side_effect=Exception("load fail")):
        calc = Calculator(config=config)
    assert calc.history == []


def test_perform_operation_trims_history(calculator):
    calculator.config.max_history_size = 2
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(1, 1)
    calculator.perform_operation(2, 2)
    calculator.perform_operation(3, 3)
    assert len(calculator.history) == 2


def test_perform_operation_reraises_operation_error(calculator):
    from unittest.mock import MagicMock
    mock_op = MagicMock()
    mock_op.execute.side_effect = OperationError("forced operation error")
    calculator.operation_strategy = mock_op
    with pytest.raises(OperationError, match="forced operation error"):
        calculator.perform_operation(1, 2)


def test_perform_operation_division_by_zero_raises(calculator):
    calculator.set_operation(OperationFactory.create_operation('divide'))
    with pytest.raises((OperationError, Exception)):
        calculator.perform_operation(1, 0)


def test_save_history_empty_writes_csv(calculator):
    assert calculator.history == []
    with patch('app.calculator.pd.DataFrame.to_csv') as mock_csv:
        calculator.save_history()
        mock_csv.assert_called_once()


def test_save_history_raises_operation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(1, 2)
    with patch('app.calculator.pd.DataFrame.to_csv', side_effect=Exception("disk full")):
        with pytest.raises(OperationError, match="Failed to save history"):
            calculator.save_history()


def test_load_history_empty_dataframe(calculator):
    with patch('app.calculator.Path.exists', return_value=True), \
         patch('app.calculator.pd.read_csv', return_value=pd.DataFrame()):
        calculator.load_history()
    assert calculator.history == []


def test_load_history_file_not_found(calculator):
    with patch('app.calculator.Path.exists', return_value=False):
        calculator.load_history()
    assert calculator.history == []


def test_load_history_raises_operation_error(calculator):
    with patch('app.calculator.Path.exists', return_value=True), \
         patch('app.calculator.pd.read_csv', side_effect=Exception("CSV corrupt")):
        with pytest.raises(OperationError, match="Failed to load history"):
            calculator.load_history()


def test_get_history_dataframe_with_entries(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    df = calculator.get_history_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1


def test_get_history_dataframe_empty(calculator):
    df = calculator.get_history_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_show_history_with_entries(calculator):
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(3, 4)
    result = calculator.show_history()
    assert len(result) == 1
    assert "12" in result[0]


def test_undo_empty(calculator):
    assert calculator.undo() is False


def test_redo_empty(calculator):
    assert calculator.redo() is False


def test_undo_restores_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(1, 2)
    calculator.perform_operation(3, 4)
    calculator.undo()
    assert len(calculator.history) == 1


def test_redo_restores_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(1, 2)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1