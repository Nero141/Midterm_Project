import datetime
from pathlib import Path
import pandas as pd
import pytest
import re
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

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

# Test Undo/Redo Functionality

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

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

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
    assert_printed(mock_print, "\nResult: 5")

def test_show_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)

    history = calculator.show_history()

    assert history == ["Addition(2, 3) = 5"]


def test_undo_empty(calculator):
    assert calculator.undo() is False


def test_redo_empty(calculator):
    assert calculator.redo() is False


@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_empty_history(mock_to_csv, calculator):
    calculator.save_history()
    mock_to_csv.assert_called_once()


@patch('app.calculator.Path.exists', return_value=False)
def test_load_history_no_file(mock_exists, calculator):
    calculator.load_history()
    assert calculator.history == []

@patch('builtins.input', side_effect=[KeyboardInterrupt(), 'exit'])
@patch('builtins.print')
def test_keyboard_exception(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "\nOperation cancelled")

@patch('builtins.input', side_effect=EOFError())
@patch('builtins.print')
def test_calculator_repl_eof_error(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "\nInput terminated. Exiting...")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.perform_operation',
       side_effect=Exception("Test error"))
def test_calculator_repl_unexpected_error(mock_operation, mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "Unexpected error: Test error")

@patch('builtins.input', side_effect=['blah', 'exit'])
@patch('builtins.print')
def test_calculator_repl_unknown_command(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "Unknown command: 'blah'. Type 'help' for available commands.")

@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.show_history', return_value=[])
def test_calculator_repl_empty_history(mock_history, mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "No calculations in history")

@patch('builtins.input', side_effect=['add', '2', '3', 'history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "\nCalculation History:")
    assert_printed(mock_print, "1. Addition(2, 3) = 5")

@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "History cleared")

@patch('builtins.input', side_effect=['add', '2', '3', 'undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "Operation undone")

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_empty(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "Nothing to undo")

@patch('builtins.input', side_effect=['add', '2', '3', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "Operation redone")

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_empty(mock_print, mock_input):
    calculator_repl()

    assert_printed(mock_print, "Nothing to redo")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.save_history')
def test_calculator_repl_save(mock_save, mock_print, mock_input):
    calculator_repl()

    mock_save.assert_called()
    assert_printed(mock_print, "History saved successfully")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.load_history')
def test_calculator_repl_load(mock_load, mock_print, mock_input):
    calculator_repl()

    mock_load.assert_called()
    assert_printed(mock_print, "History loaded successfully")

def strip_ansi(text):
    """Remove ANSI color codes from terminal output."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def assert_printed(mock_print, expected):
    """Check printed output while ignoring color codes."""
    printed_messages = [
        strip_ansi(str(call.args[0]))
        for call in mock_print.call_args_list
        if call.args
    ]

    assert expected in printed_messages
    
@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.perform_operation',
       return_value=5)
def test_calculator_repl_non_decimal_result(
        mock_operation, mock_print, mock_input):

    calculator_repl()

    assert_printed(mock_print, "\nResult: 5")
    
@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.save_history', side_effect=Exception('Disk full'))
def test_repl_exit_save_failure(mock_save, mock_print, mock_input):
    calculator_repl()
    assert_printed(mock_print, '\nWarning: Could not save history: Disk full')
    assert_printed(mock_print, 'Goodbye!')


@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.save_history')
def test_repl_manual_save_failure(mock_save, mock_print, mock_input):
    mock_save.side_effect = [Exception('Save failed'), None]
    calculator_repl()
    assert_printed(mock_print, 'Error saving history: Save failed')


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator.load_history', side_effect=Exception('Load failed'))
def test_repl_load_failure(mock_load, mock_print, mock_input):
    calculator_repl()
    assert_printed(mock_print, 'Error loading history: Load failed')


@pytest.mark.parametrize('inputs', [
    ['add', 'cancel', 'exit'],
    ['add', '2', 'cancel', 'exit'],
])
def test_repl_cancel_number(inputs):
    with patch('builtins.input', side_effect=inputs), patch('builtins.print') as mock_print:
        calculator_repl()
    assert_printed(mock_print, 'Operation cancelled')


@patch('builtins.input', side_effect=['add', 'invalid', '3', 'exit'])
@patch('builtins.print')
def test_repl_invalid_number(mock_print, mock_input):
    calculator_repl()
    assert any('Error: Invalid number format' in strip_ansi(str(c.args[0]))
               for c in mock_print.call_args_list if c.args)


@patch('builtins.input', side_effect=[Exception('Input failure'), 'exit'])
@patch('builtins.print')
def test_repl_command_input_failure(mock_print, mock_input):
    calculator_repl()
    assert_printed(mock_print, 'Error: Input failure')


@patch('builtins.print')
@patch('app.calculator_repl.logging.error')
@patch('app.calculator_repl.Calculator', side_effect=Exception('Initialization failed'))
def test_repl_initialization_failure(mock_calculator, mock_logging, mock_print):
    with pytest.raises(Exception, match='Initialization failed'):
        calculator_repl()
    assert_printed(mock_print, 'Fatal error: Initialization failed')
    mock_logging.assert_called_once()
