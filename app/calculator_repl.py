########################
# Calculator REPL       #
########################

import os
import logging
from decimal import Decimal

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory

# Optional A feature: color-coded output (disabled automatically during pytest)
USE_COLOR = ("PYTEST_CURRENT_TEST" not in os.environ)
if USE_COLOR:
    from colorama import Fore, Style, init
    init(autoreset=True)
else:
    class _NoColor:  # pragma: no cover
        def __getattr__(self, name):
            return ""
    Fore = Style = _NoColor()


OPS = [
    "add", "subtract", "multiply", "divide",
    "power", "root",
    "modulus", "int_divide", "percent", "abs_diff",
]

HELP_TEXT = """
Available commands:
  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff
  history   - Show calculation history
  clear     - Clear calculation history
  undo      - Undo the last calculation
  redo      - Redo the last undone calculation
  save      - Save calculation history to file
  load      - Load calculation history from file
  help      - Show this help menu
  exit      - Save history and exit
""".strip()


def _prompt_number(prompt: str) -> str:
    value = input(prompt).strip()
    if value.lower() == "cancel":
        raise KeyboardInterrupt
    return value


def calculator_repl() -> None:
    calc = Calculator()
    calc.add_observer(LoggingObserver())
    calc.add_observer(AutoSaveObserver(calc))

    print(Fore.YELLOW + "Calculator started. Type 'help' for commands." + Style.RESET_ALL)

    while True:
        try:
            command = input("\nEnter command: ").lower().strip()
            if not command:
                continue

            if command == "help":
                print(HELP_TEXT)
                continue

            if command == "exit":
                try:
                    calc.save_history()
                    print(Fore.YELLOW + "History saved successfully." + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.YELLOW + f"Warning: Could not save history: {e}" + Style.RESET_ALL)
                print("Goodbye!")
                return

            if command == "history":
                history = calc.show_history()
                if not history:
                    print(Fore.YELLOW + "No calculations in history." + Style.RESET_ALL)
                else:
                    print("\nCalculation History:")
                    for i, entry in enumerate(history, 1):
                        print(f"{i}. {entry}")
                continue

            if command == "clear":
                calc.clear_history()
                print(Fore.YELLOW + "History cleared." + Style.RESET_ALL)
                continue

            if command == "undo":
                print(
                    Fore.YELLOW + ("Operation undone." if calc.undo() else "Nothing to undo.")
                    + Style.RESET_ALL
                )
                continue

            if command == "redo":
                print(
                    Fore.YELLOW + ("Operation redone." if calc.redo() else "Nothing to redo.")
                    + Style.RESET_ALL
                )
                continue

            if command == "save":
                calc.save_history()
                print(Fore.YELLOW + "History saved successfully." + Style.RESET_ALL)
                continue

            if command == "load":
                calc.load_history()
                print(Fore.YELLOW + "History loaded successfully." + Style.RESET_ALL)
                continue

            if command in OPS:
                print("\nEnter numbers (or 'cancel' to abort):")
                a = _prompt_number("First number: ")
                b = _prompt_number("Second number: ")

                operation = OperationFactory.create_operation(command)
                calc.set_operation(operation)

                result = calc.perform_operation(a, b)
                if isinstance(result, Decimal):
                    result = result.normalize()

                print(Fore.GREEN + f"\nResult: {result}" + Style.RESET_ALL)
                continue

            print(Fore.RED + f"Unknown command: '{command}'. Type 'help' for available commands." + Style.RESET_ALL)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nOperation cancelled." + Style.RESET_ALL)
            continue
        except (ValidationError, OperationError) as e:
            print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
            logging.error(f"REPL error: {e}")
            continue
        except EOFError:
            print("\nInput terminated. Exiting...")
            return
        except Exception as e:  # pragma: no cover
            print(Fore.RED + f"Unexpected error: {e}" + Style.RESET_ALL)  # pragma: no cover
            logging.exception("Unexpected REPL error")  # pragma: no cover
            raise