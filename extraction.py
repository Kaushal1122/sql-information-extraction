import argparse
import json
import logging
import re
import sys
from pathlib import Path

from config import load_config
from logger import setup_logging

PROCEDURE_PATTERN = re.compile(
    r"CREATE\s+PROCEDURE\s+[`\"]?(\w+)[`\"]?\s*"
    r"\((.*?)\)\s*BEGIN\b",
    re.IGNORECASE | re.DOTALL
)

PARAMETER_PATTERN = re.compile(
    r"\b(INOUT|IN|OUT)\s+"
    r"[`\"]?(\w+)[`\"]?\s+"
    r"([A-Z][A-Z0-9_]*(?:\s*\([^)]*\))?)",
    re.IGNORECASE
)


def read_sql_file(file_path: Path, encoding: str) -> str:
    """Read SQL content from the supplied file."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"SQL file not found: {file_path}"
        )

    return file_path.read_text(encoding=encoding)


def extract_parameters(parameter_text: str) -> list[dict]:
    """Extract parameter directions, names and data types."""
    parameters = []

    for match in PARAMETER_PATTERN.finditer(parameter_text):
        parameters.append({
            "direction": match.group(1).upper(),
            "name": match.group(2),
            "type": re.sub(
                r"\s+",
                " ",
                match.group(3).strip().upper()
            )
        })

    return parameters


def extract_procedures(sql_content: str) -> list[dict]:
    """Extract stored procedure information from SQL content."""
    procedures = []

    for match in PROCEDURE_PATTERN.finditer(sql_content):
        procedure_name = match.group(1)
        parameter_text = match.group(2)

        procedures.append({
            "name": procedure_name,
            "parameters": extract_parameters(parameter_text)
        })

    return procedures


def write_json_file(
    output_path: Path,
    data: dict,
    encoding: str,
    indent: int
) -> None:
    """Write extracted information into a JSON file."""
    with output_path.open("w", encoding=encoding) as file:
        json.dump(data, file, indent=indent)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract stored procedure information from a SQL file."
    )

    parser.add_argument(
        "sql_file",
        type=Path,
        help="Path to the input SQL file."
    )

    return parser.parse_args()


def main() -> int:
    """Run the SQL information extraction application."""
    logger = logging.getLogger("sql_information_extraction")

    try:
        config = load_config()
        logger = setup_logging(config["logging"])

        args = parse_arguments()
        input_path = args.sql_file

        input_encoding = config["application"]["input_encoding"]
        output_encoding = config["application"]["output_encoding"]
        output_indent = config["application"]["output_indent"]

        logger.info("Starting SQL extraction: %s", input_path)

        sql_content = read_sql_file(input_path, input_encoding)
        procedures = extract_procedures(sql_content)

        if not procedures:
            logger.warning(
                "No stored procedures found in %s",
                input_path
            )

        output_data = {
            "procedures": procedures
        }

        output_path = input_path.with_suffix(".json")

        write_json_file(
            output_path,
            output_data,
            output_encoding,
            output_indent
        )

        logger.info(
            "Extracted %d stored procedures.",
            len(procedures)
        )
        logger.info("JSON output created: %s", output_path)

        return 0

    except FileNotFoundError as error:
        logger.exception("File not found: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return 1

    except (ValueError, KeyError) as error:
        logger.exception("Configuration error: %s", error)
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    except UnicodeDecodeError as error:
        logger.exception("Encoding error: %s", error)
        print(f"Encoding error: {error}", file=sys.stderr)
        return 1

    except OSError as error:
        logger.exception("File operation error: %s", error)
        print(f"File operation error: {error}", file=sys.stderr)
        return 1

    except Exception:
        logger.exception("An unexpected error occurred.")
        print(
            "An unexpected error occurred. Check the application logs.",
            file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
