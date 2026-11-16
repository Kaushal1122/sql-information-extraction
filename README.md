# SQL Information Extraction

A Python script that extracts stored procedure information from SQL files using regular expressions and generates a corresponding JSON file.

The repository includes a sample SQL input file (`sample_stored_procedure.sql`) and its generated JSON output (`sample_stored_procedure.json`) for reference.

## Prerequisites

- Python 3.13 or later
- Git

## Setup

Clone the repository:

```bash
git clone https://github.com/Kaushal1122/sql-information-extraction.git
cd sql-information-extraction
```

Create and activate a virtual environment:

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the script by providing the path to a SQL file:

```bash
python extraction.py sample_stored_procedure.sql
```

The script generates a corresponding JSON file in the same directory:

```text
sample_stored_procedure.json
```

The JSON output contains the extracted stored procedure names and their parameters, including parameter directions and data types.

## Testing

Run the unit tests with coverage:

```bash
python -m pytest -v --cov=extraction --cov-report=term-missing
```

## Code Quality

Check code quality and formatting using Ruff:

```bash
python -m ruff check .
```

## Configuration

Application settings and logging parameters can be modified in `config.yaml`.