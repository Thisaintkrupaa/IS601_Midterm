########################
# Calculator REPL
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


# Symbols for nicer output
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

# Optional A feature: color output
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
  add, subtract, multiply, divide
  power, root, modulus, int_divide, percent, abs_diff

  history   - Show calculation history
  stats     - Show statistics about calculations
  clear     - Clear history
  undo      - Undo last calculation
  redo      - Redo last undone calculation
  save      - Save history to CSV
  load      - Load history from CSV
  help      - Show commands
  exit      - Exit calculator
"""


def calculator_repl():
    calc = Calculator()

    calc.add_observer(LoggingObserver())
    calc.add_observer(AutoSaveObserver(calc))

    print(Fore.YELLOW + "=" * 40)
    print("   Advanced Calculator (IS601)")
    print("=" * 40 + Style.RESET_ALL)
    print("Type 'help' for commands.")

    while True:
        try:
            command = input(Fore.CYAN + "\ncalc> " + Style.RESET_ALL).lower().strip()

            if not command:
                continue

            if command == "help":
                print(HELP_TEXT)
                continue

            if command == "exit":
                try:
                    calc.save_history()
                    print(Fore.YELLOW + "History saved." + Style.RESET_ALL)
                except Exception as e:
                    print(Fore.YELLOW + f"Warning: could not save history: {e}")
                print("Goodbye!")
                return

            if command == "history":
                history = calc.show_history()
                if not history:
                    print(Fore.YELLOW + "No calculations in history.")
                else:
                    print("\nHistory:")
                    for i, entry in enumerate(history, 1):
                        print(f"{i}. {entry}")
                continue

            # ⭐ NEW FEATURE
            if command == "stats":
                history = calc.history

                if not history:
                    print(Fore.YELLOW + "No calculations yet.")
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

            if command == "clear":
                calc.clear_history()
                print(Fore.YELLOW + "History cleared.")
                continue

            if command == "undo":
                if calc.undo():
                    print(Fore.YELLOW + "Undo successful.")
                else:
                    print(Fore.YELLOW + "Nothing to undo.")
                continue

            if command == "redo":
                if calc.redo():
                    print(Fore.YELLOW + "Redo successful.")
                else:
                    print(Fore.YELLOW + "Nothing to redo.")
                continue

            if command == "save":
                calc.save_history()
                print(Fore.YELLOW + "History saved.")
                continue

            if command == "load":
                calc.load_history()
                print(Fore.YELLOW + "History loaded.")
                continue

            if command in OPS:

                print("Enter numbers (or 'cancel')")

                a = input("First number: ")
                if a.lower() == "cancel":
                    continue

                b = input("Second number: ")
                if b.lower() == "cancel":
                    continue

                operation = OperationFactory.create_operation(command)
                calc.set_operation(operation)

                result = calc.perform_operation(a, b)

                if isinstance(result, Decimal):
                    result = result.normalize()

                symbol = OP_SYMBOLS.get(command, "?")

                print(
                    Fore.GREEN
                    + f"\n{a} {symbol} {b} = {result}"
                    + Style.RESET_ALL
                )

                continue

            print(Fore.RED + f"Unknown command: {command}")



        except (ValidationError, OperationError) as e:
            print(Fore.RED + f"Error: {e}")
            logging.error(f"Operation error: {e}")

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nOperation cancelled")
            continue

        except EOFError:
            print("\nInput terminated. Exiting...")
            return

        except Exception as e:  # pragma: no cover
            print(Fore.RED + f"Unexpected error: {e}")
            logging.exception("Unexpected REPL error")
            raise

        