# Python Calcultor Application   

A command-line calculator built using Python. This project supports basic and advanced arthimetic operations, calculation history, undo/redo functionality, logging, and automated testing. Using object-oriented programming and design patterns to keep the code organized.

---

# Project Setup

## 1. Install Python

Make sure Python 3.10 or higher is installed.

Download Python: https://www.python.org/downloads/

**Verify Python:**

```bash
python --version
```

---

## 2. Clone the Repository

Clone the project from GitHub:

```bash
git clone < repository-url >
cd < repository-directory >
```

---

## 3. Create a Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

**Activate it (Windows):**

```bash
venv\Scripts\activate
```

**Activate it (Linux/WSL/Mac):**

```bash
source venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

---

# 4. Running the Calculator

Start the application:

```bash
python main.py
```

The calculator runs through a command-line interface where users can select operations and enter numbers.

---

# 5. Calculator Operations

The calculator project includes the following arithmetic operations:

| Command | Description |
|---------|-------------|
| add | Addition |
| subtract | Subtraction |
| multiply | Multiplication |
| divide | Division |
| power | Exponentiation |
| root | Nth root |
| modulus | Remainder |
| intdivide | Integer division |
| percent | Percentage calculation |
| absdiff | Absolute difference |

Each operation accepts two numerical inputs.

---

# 6. History Management

The calculator supports calculation history and uses the Memento Design Pattern for undo and redo functionality.

| Command | Description |
|---------|-------------|
| history | Display calculation history |
| clear | Clear calculation history |
| undo | Undo the previous calculation |
| redo | Redo an undone calculation |
| save | Save history to a CSV file |
| load | Load history from a CSV file |
| help | Display available commands |
| exit | Exit the calculator |

Calculation history is managed using pandas and can be saved or loaded from CSV files.

---

# 7. Design Patterns and Configuration

The project uses three main design patterns:

- **Factory Pattern:** Creates different arithmetic operation objects.
- **Memento Pattern:** Manages calculation history and undo/redo functionality.
- **Observer Pattern:** Handles logging and automatic history saving.

Environment variables are managed using a `.env` file to configure settings such as calculation precision, history size, and logging.

---

# 8. Testing

The project uses pytest for automated testing.

**Run all tests:**

```bash
pytest
```

**Run tests with coverage:**

```bash
pytest --cov=app --cov-report=term-missing
```

**Verify 90% test coverage:**

```bash
pytest --cov=app --cov-fail-under=90
```

GitHub Actions is used to automatically run tests when changes are pushed to the repository.

---

# 9. Submission Instructions

After completing the project, commit and push your changes to GitHub.

```bash
git add .
git commit -m "Complete Calculator Assignment"
git push origin main
```

Submit your GitHub repository link as instructed.

---

# 🔥 Useful Commands Cheat Sheet

| Action | Command |
|--------|---------|
| Check Python version | `python --version` |
| Clone repository | `git clone <repository-url>` |
| Create virtual environment | `python -m venv venv` |
| Install dependencies | `pip install -r requirements.txt` |
| Run calculator | `python main.py` |
| Run tests | `pytest` |
| Check coverage | `pytest --cov=app` |
| Push changes | `git push origin main` |

---

# Notes

- Python 3.10+ is recommended.
- Use a virtual environment to manage dependencies.
- The calculator uses pandas for history management.
- Logging and error handling help manage invalid operations.
- GitHub Actions helps maintain code quality through automated testing.

---