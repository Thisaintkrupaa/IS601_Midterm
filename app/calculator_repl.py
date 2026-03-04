########################
# Calculator REPL       #
########################

import os
import logging
from decimal import Decimal
from collections import Counter

import pandas as pd

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory


USE_COLOR = ("PYTEST_CURRENT_TEST" not in os.environ)

if USE_COLOR:  # pragma: no cover
    from colorama import Fore, Style, init
    init(autoreset=True)
else:  # pragma: no cover
    class _NoColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = _NoColor()


OPS = [
    "add", "subtract", "multiply", "divide",
    "power", "root",
    "modulus", "int_divide", "percent", "abs_diff",
]

OP_SYMBOLS = {
    "add": "+",
    "subtract": "-",
    "multiply": "*",
    "divide": "/",
    "power": "^",
    "root": "√",
    "modulus": "%",
    "int_divide": "//",
    "percent": "%",
    "abs_diff": "|-|",
}


def calculator_repl():
    try:
        calc = Calculator()

        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(Fore.YELLOW + "Calculator started. Type 'help' for commands." + Style.RESET_ALL)

        while True:
            try:
                command = input(Fore.CYAN + "\nEnter command: " + Style.RESET_ALL).lower().strip()

                if command == 'help':
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff")
                    print("  history - Show calculation history")
                    print("  stats - Show statistics about calculations")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue

                if command == 'exit':
                    try:
                        calc.save_history()
                        print(Fore.YELLOW + "History saved successfully." + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.YELLOW + f"Warning: Could not save history: {e}" + Style.RESET_ALL)
                    print("Goodbye!")
                    break

                if command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(Fore.YELLOW + "No calculations in history" + Style.RESET_ALL)
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == "stats":
                    history = calc.history
                    if not history:
                        print(Fore.YELLOW + "No calculations yet." + Style.RESET_ALL)
                        continue

                    df = pd.DataFrame([c.to_dict() for c in history])
                    total = len(df)
                    last_result = df.iloc[-1]["result"]
                    most_used = Counter(df["operation"]).most_common(1)[0][0]

                    print(Fore.GREEN + "\nCalculator Statistics")
                    print("----------------------")
                    print(f"Total calculations : {total}")
                    print(f"Last result        : {last_result}")
                    print(f"Most used operation: {most_used}")
                    print(Style.RESET_ALL)
                    continue

                if command == 'clear':
                    calc.clear_history()
                    print(Fore.YELLOW + "History cleared" + Style.RESET_ALL)
                    continue

                if command == 'undo':
                    if calc.undo():
                        print(Fore.YELLOW + "Operation undone" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to undo" + Style.RESET_ALL)
                    continue

                if command == 'redo':
                    if calc.redo():
                        print(Fore.YELLOW + "Operation redone" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to redo" + Style.RESET_ALL)
                    continue

                if command == 'save':
                    try:
                        calc.save_history()
                        print(Fore.YELLOW + "History saved successfully" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Error saving history: {e}" + Style.RESET_ALL)
                    continue

                if command == 'load':
                    try:
                        calc.load_history()
                        print(Fore.YELLOW + "History loaded successfully" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Error loading history: {e}" + Style.RESET_ALL)
                    continue

                if command in OPS:
                    print("\nEnter numbers (or 'cancel' to abort):")

                    a = input("First number: ")
                    if a.lower() == 'cancel':
                        print(Fore.YELLOW + "Operation cancelled" + Style.RESET_ALL)
                        continue

                    b = input("Second number: ")
                    if b.lower() == 'cancel':
                        print(Fore.YELLOW + "Operation cancelled" + Style.RESET_ALL)
                        continue

                    operation = OperationFactory.create_operation(command)
                    calc.set_operation(operation)

                    result = calc.perform_operation(a, b)

                    if isinstance(result, Decimal):
                        result = result.normalize()
                        if 'E' in str(result) or 'e' in str(result):  # pragma: no cover
                            result = f"{result:f}".rstrip('0').rstrip('.')

                    symbol = OP_SYMBOLS.get(command, "?")

                    print(
                        Fore.GREEN
                        + f"\n{a} {symbol} {b} = {result}"
                        + Style.RESET_ALL
                    )
                    continue

                print(Fore.RED + f"Unknown command: '{command}'. Type 'help' for available commands." + Style.RESET_ALL)

            except (ValidationError, OperationError) as e:
                print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                logging.error(f"Operation error: {e}")

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nOperation cancelled" + Style.RESET_ALL)
                continue

            except EOFError:
                print("\nInput terminated. Exiting...")
                break

            except Exception as e:  # pragma: no cover
                print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                continue

    except Exception as e:  # pragma: no cover
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise