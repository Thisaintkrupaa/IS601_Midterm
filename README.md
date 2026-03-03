# IS601 Midterm Project - Enhanced Calculator

A command-line calculator application built with Python, featuring a REPL interface, multiple design patterns, pandas-based history management, and robust configuration via environment variables.

---

## 📋 Table of Contents

- [Project Description](#project-description)
- [Project Structure](#project-structure)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Configuration Setup (.env)](#configuration-setup-env)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Design Patterns Explained](#design-patterns-explained)
- [Error Handling](#error-handling)
- [Running Tests](#running-tests)
- [CI/CD](#cicd)

---

## 📖 Project Description

This enhanced calculator application extends a basic arithmetic tool into a fully-featured, design-pattern-driven REPL application. It supports ten arithmetic operations, undo/redo history management, observer-based logging and auto-saving, configurable behavior via a `.env` file, and comprehensive unit testing with 90%+ coverage enforced through GitHub Actions CI/CD.

Key highlights:
- **10 arithmetic operations** including power, root, modulus, integer division, percentage, and absolute difference
- **Undo/Redo** via the Memento Pattern
- **Auto-save & logging** via the Observer Pattern
- **Configurable** via environment variables using `python-dotenv`
- **Persistent history** using `pandas` DataFrames serialized to CSV
- **90%+ test coverage** enforced in CI

---

## 📁 Project Structure

```
Assignment5/
├── app/
│   ├── __init__.py
│   ├── calculation.py          # Calculation data class (operation, operands, result, timestamp)
│   ├── calculator.py           # Core calculator logic with observer support
│   ├── calculator_config.py    # Configuration loader using python-dotenv
│   ├── calculator_memento.py   # Memento pattern for undo/redo
│   ├── calculator_repl.py      # REPL command-line interface
│   ├── exceptions.py           # Custom exceptions: OperationError, ValidationError
│   ├── history.py              # Pandas-based history manager with CSV persistence
│   ├── input_validators.py     # Input validation utilities
│   ├── logger.py               # Logging configuration and LoggingObserver
│   └── operations.py           # All operation strategies + Factory
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_calculation.py
│   ├── test_calculator.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_history.py
│   ├── test_operations.py
│   └── test_validators.py
├── .github/
│   └── workflows/
│       └── python-app.yml      # GitHub Actions CI/CD workflow
├── .env                        # Environment variable configuration (do not commit secrets)
├── .gitignore
├── main.py                     # Application entry point
├── requirements.txt
└── README.md
```

---

## ✨ Features

### Arithmetic Operations

| Operation           | Command        | Description                                   |
|---------------------|----------------|-----------------------------------------------|
| Addition            | `add`          | `a + b`                                       |
| Subtraction         | `subtract`     | `a - b`                                       |
| Multiplication      | `multiply`     | `a * b`                                       |
| Division            | `divide`       | `a / b` (raises error on divide-by-zero)      |
| Power               | `power`        | `a ^ b`                                       |
| Root                | `root`         | `b`th root of `a`                             |
| Modulus             | `modulus`      | `a % b`                                       |
| Integer Division    | `int_divide`   | `a // b`                                      |
| Percentage          | `percent`      | `(a / b) * 100`                               |
| Absolute Difference | `abs_diff`     | `|a - b|`                                     |

### Design Patterns

- **Factory Pattern** — `OperationFactory` creates the correct operation instance from a string command
- **Strategy Pattern** — Each operation is an interchangeable strategy class
- **Observer Pattern** — `LoggingObserver` and `AutoSaveObserver` respond to new calculations
- **Memento Pattern** — Captures and restores calculator history state for undo/redo
- **Facade Pattern** — Simplified interface to the subsystem through `calculator_repl.py`

### History Management

- Stores all calculations as `Calculation` instances (operation, operands, result, timestamp)
- Uses a `pandas` DataFrame as the in-memory store
- Auto-saves to a CSV file on every new calculation (configurable)
- Loads history from CSV on startup
- Undo/redo stacks maintained via the Memento pattern

### Logging

- Logs all calculations, errors, and events using Python's `logging` module
- Log level and output file configured via `.env`
- `LoggingObserver` writes INFO-level entries for each new calculation
- Errors logged at WARNING or ERROR level with full context

---

## 🛠️ Setup Instructions

### 1. Install Homebrew (Mac Only)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew --version
```

### 2. Install Git

**Mac:**
```bash
brew install git
```

**Windows:** Download from [git-scm.com](https://git-scm.com/download/win)

Configure Git:
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### 3. Set Up SSH Key for GitHub

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub | pbcopy   # Mac only
```

Go to [GitHub SSH Settings](https://github.com/settings/keys) → **New SSH Key** → paste and save.

```bash
ssh -T git@github.com
```

### 4. Clone the Repository

```bash
git clone git@github.com:Thisaintkrupaa/IS601_Assignment5.git
cd IS601_Assignment5
```

### 5. Install Python 3.10+

**Mac:**
```bash
brew install python
python3 --version
```

**Windows:** Download from [python.org](https://www.python.org/downloads/) and check **Add Python to PATH**.

### 6. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate.bat       # Windows
```

### 7. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration Setup (.env)

Create a `.env` file in the project root. The app uses `python-dotenv` to load these settings at startup. All values have sensible defaults if not provided.

```dotenv
# --- Directory Settings ---
CALCULATOR_LOG_DIR=logs                  # Directory where log files are written
CALCULATOR_HISTORY_DIR=history           # Directory where CSV history is saved

# --- History Settings ---
CALCULATOR_MAX_HISTORY_SIZE=100          # Max number of entries to keep in history
CALCULATOR_AUTO_SAVE=true                # Auto-save after every calculation (true/false)
CALCULATOR_HISTORY_FILE=history/calc_history.csv   # Path to the history CSV file

# --- Calculation Settings ---
CALCULATOR_PRECISION=10                  # Decimal precision for results
CALCULATOR_MAX_INPUT_VALUE=1000000       # Maximum allowed numeric input
CALCULATOR_DEFAULT_ENCODING=utf-8        # File encoding for CSV and logs

# --- Logging Settings ---
CALCULATOR_LOG_FILE=logs/calculator.log  # Path to the log output file
CALCULATOR_LOG_LEVEL=INFO                # Logging level: DEBUG, INFO, WARNING, ERROR
```

> **Note:** The `.env` file is listed in `.gitignore` and should never be committed to version control if it contains sensitive values.

The `calculator_config.py` module loads and validates all settings on startup, providing default values for any missing variables.

---

## 🚀 Running the Application

```bash
python main.py
```

The REPL will start and display a welcome message. Type `help` to see all available commands.

---

## 📖 Usage Guide

### Performing Calculations

Enter the operation name followed by two numbers:

```
calc> add 10 5
Result: 15.0

calc> power 2 8
Result: 256.0

calc> percent 45 200
Result: 22.5

calc> root 27 3
Result: 3.0

calc> abs_diff 10 -4
Result: 14.0
```

### REPL Commands

| Command      | Description                                      |
|--------------|--------------------------------------------------|
| `help`       | Display all available commands and operations    |
| `history`    | Display full calculation history                 |
| `undo`       | Undo the last calculation                        |
| `redo`       | Redo the last undone calculation                 |
| `save`       | Manually save history to CSV                     |
| `load`       | Load history from CSV                            |
| `clear`      | Clear all calculation history                    |
| `exit`       | Exit the application                             |

### Example Session

```
calc> add 100 200
Result: 300.0

calc> multiply 3 4
Result: 12.0

calc> history
[1] add(100.0, 200.0) = 300.0  @ 2025-01-01 10:00:00
[2] multiply(3.0, 4.0) = 12.0  @ 2025-01-01 10:00:05

calc> undo
Undone: multiply(3.0, 4.0) = 12.0

calc> redo
Redone: multiply(3.0, 4.0) = 12.0

calc> save
History saved to history/calc_history.csv

calc> exit
Goodbye!
```

### Error Examples

```
calc> divide 10 0
Error: Division by zero is not allowed.

calc> add abc 5
Error: Invalid input. Please enter numerical values.

calc> add 9999999999999999999 1
Error: Input value exceeds the maximum allowed limit.
```

---

## 🧩 Design Patterns Explained

### Factory Pattern (`operations.py`)

`OperationFactory.create(operation_name)` returns the correct strategy object based on the command string. Adding a new operation only requires registering it in the factory map — no changes to the REPL or calculator core.

### Strategy Pattern (`operations.py`)

Each operation (`AddOperation`, `PowerOperation`, `ModulusOperation`, etc.) implements a common `execute(a, b)` interface. The calculator calls `operation.execute(a, b)` without knowing the specific type, making operations swappable at runtime.

### Observer Pattern (`calculator.py`, `logger.py`, `history.py`)

The `Calculator` class maintains a list of observers. After each calculation, it calls `notify_observers(calculation)`. Two observers are registered by default:

- **`LoggingObserver`** — Writes a log entry to the configured log file
- **`AutoSaveObserver`** — Saves the updated history DataFrame to CSV (when `CALCULATOR_AUTO_SAVE=true`)

### Memento Pattern (`calculator_memento.py`)

`CalculatorMemento` captures a snapshot of the history list. `undo()` pops from the undo stack and pushes to the redo stack; `redo()` does the reverse. This allows full traversal of the history timeline without modifying the core data store.

### Facade Pattern (`calculator_repl.py`)

The REPL acts as a simplified interface to the subsystem. Users interact with a small set of text commands; the REPL delegates to `Calculator`, `HistoryManager`, `OperationFactory`, and `CalculatorConfig` without exposing their internals.

---

## 🚨 Error Handling

The application uses two custom exception types defined in `exceptions.py`:

- **`OperationError`** — Raised for mathematical errors (division by zero, invalid root, etc.)
- **`ValidationError`** — Raised for invalid inputs (non-numeric, out-of-range values)

Both LBYL ("Look Before You Leap") and EAFP ("Easier to Ask Forgiveness than Permission") paradigms are used:

- **LBYL**: Input range and type checks in `input_validators.py` before executing operations
- **EAFP**: Try/except blocks in the REPL and history loader to handle unexpected file or runtime errors gracefully

All exceptions produce user-friendly messages in the REPL and are logged at the appropriate level.

---

## 🧪 Running Tests

Run all tests with coverage:

```bash
pytest --cov=app tests/
```

Check the detailed coverage report:

```bash
coverage report -m
```

Enforce a minimum of 90% coverage (fails if below):

```bash
pytest --cov=app --cov-fail-under=90 tests/
```

Tests cover:
- All 10 arithmetic operations (including edge cases like zero division, negative exponents)
- Undo/redo stack behavior
- Observer notification and side effects
- History serialization and deserialization (including malformed CSV)
- Configuration loading with missing and invalid values
- Input validation boundaries

Lines intentionally excluded from coverage are marked with `# pragma: no cover` (e.g., unreachable `pass` branches).

---

## ⚙️ CI/CD

This project uses **GitHub Actions** to automatically run tests on every push or pull request to `main`.

### What the Pipeline Does

1. Checks out the repository
2. Sets up Python 3.x
3. Installs all dependencies from `requirements.txt`
4. Runs `pytest` with `pytest-cov`
5. **Fails the build** if test coverage drops below 90%

### Workflow File (`.github/workflows/python-app.yml`)

```yaml
name: Python application

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Check out the code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage enforcement
        run: |
          pytest --cov=app --cov-fail-under=90
```

---

## 🔥 Quick Commands Cheat Sheet

| Action                        | Command                                        |
|-------------------------------|------------------------------------------------|
| Activate virtual environment  | `source venv/bin/activate`                     |
| Install packages              | `pip install -r requirements.txt`              |
| Run application               | `python main.py`                               |
| Run tests with coverage       | `pytest --cov=app tests/`                      |
| Enforce 90% coverage          | `pytest --cov=app --cov-fail-under=90 tests/`  |
| Push to GitHub                | `git add . && git commit -m "msg" && git push` |

---

