import json
import logging
import sys

import pytest

import extraction
from extraction import (
    extract_parameters,
    extract_procedures,
    read_sql_file,
    write_json_file,
)


def test_extract_parameters():
    parameter_text = """
        IN customerId INT,
        IN startDate DATE,
        OUT newStock INT,
        INOUT quantity INT,
        IN salary DECIMAL(10,2),
        IN firstName VARCHAR(50)
    """

    result = extract_parameters(parameter_text)

    assert len(result) == 6
    assert result[0] == {
        "direction": "IN",
        "name": "customerId",
        "type": "INT"
    }
    assert result[2] == {
        "direction": "OUT",
        "name": "newStock",
        "type": "INT"
    }
    assert result[3] == {
        "direction": "INOUT",
        "name": "quantity",
        "type": "INT"
    }
    assert result[4]["type"] == "DECIMAL(10,2)"
    assert result[5]["type"] == "VARCHAR(50)"


def test_extract_procedures():
    sql_content = """
        CREATE PROCEDURE GetCustomerOrders(
            IN customerId INT,
            IN startDate DATE
        )
        BEGIN
            SELECT * FROM orders;
        END //

        CREATE PROCEDURE UpdateProductStock(
            IN productId INT,
            OUT newStock INT
        )
        BEGIN
            UPDATE products SET stock = 10;
        END //
    """

    result = extract_procedures(sql_content)

    assert len(result) == 2
    assert result[0]["name"] == "GetCustomerOrders"
    assert len(result[0]["parameters"]) == 2
    assert result[1]["name"] == "UpdateProductStock"
    assert result[1]["parameters"][1]["direction"] == "OUT"


def test_extract_procedures_with_no_parameters():
    sql_content = """
        CREATE PROCEDURE GetAllCustomers()
        BEGIN
            SELECT * FROM customers;
        END //
    """

    result = extract_procedures(sql_content)

    assert result == [
        {
            "name": "GetAllCustomers",
            "parameters": []
        }
    ]


def test_extract_procedures_with_no_procedures():
    sql_content = "SELECT * FROM customers;"

    result = extract_procedures(sql_content)

    assert result == []


def test_read_sql_file(tmp_path):
    sql_file = tmp_path / "sample.sql"
    sql_file.write_text(
        "CREATE PROCEDURE TestProcedure() BEGIN SELECT 1; END",
        encoding="utf-8"
    )

    result = read_sql_file(sql_file, "utf-8")

    assert "CREATE PROCEDURE TestProcedure" in result


def test_read_sql_file_not_found(tmp_path):
    sql_file = tmp_path / "missing.sql"

    with pytest.raises(FileNotFoundError):
        read_sql_file(sql_file, "utf-8")


def test_write_json_file(tmp_path):
    output_file = tmp_path / "output.json"
    data = {
        "procedures": [
            {
                "name": "TestProcedure",
                "parameters": [
                    {
                        "direction": "IN",
                        "name": "customerId",
                        "type": "INT"
                    }
                ]
            }
        ]
    }

    write_json_file(output_file, data, "utf-8", 4)

    result = json.loads(output_file.read_text(encoding="utf-8"))

    assert result == data


def test_main_success(tmp_path, monkeypatch):
    sql_file = tmp_path / "sample.sql"
    sql_file.write_text(
        """
        CREATE PROCEDURE TestProcedure(IN customerId INT)
        BEGIN
            SELECT * FROM customers;
        END //
        """,
        encoding="utf-8"
    )

    config = {
        "application": {
            "input_encoding": "utf-8",
            "output_encoding": "utf-8",
            "output_indent": 4
        },
        "logging": {
            "level": "INFO",
            "format": "%(message)s",
            "file": "extraction.log"
        }
    }

    monkeypatch.setattr(
        extraction,
        "load_config",
        lambda: config
    )
    monkeypatch.setattr(
        extraction,
        "setup_logging",
        lambda logging_config: logging.getLogger("test")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["extraction.py", str(sql_file)]
    )

    result = extraction.main()

    output_file = tmp_path / "sample.json"
    output_data = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert result == 0
    assert output_file.is_file()
    assert output_data["procedures"][0]["name"] == (
        "TestProcedure"
    )


def test_main_missing_sql_file(tmp_path, monkeypatch, capsys):
    sql_file = tmp_path / "missing.sql"

    config = {
        "application": {
            "input_encoding": "utf-8",
            "output_encoding": "utf-8",
            "output_indent": 4
        },
        "logging": {
            "level": "INFO",
            "format": "%(message)s",
            "file": "extraction.log"
        }
    }

    monkeypatch.setattr(
        extraction,
        "load_config",
        lambda: config
    )
    monkeypatch.setattr(
        extraction,
        "setup_logging",
        lambda logging_config: logging.getLogger("test")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["extraction.py", str(sql_file)]
    )

    result = extraction.main()

    captured = capsys.readouterr()

    assert result == 1
    assert "SQL file not found" in captured.err


def test_main_without_procedures(tmp_path, monkeypatch):
    sql_file = tmp_path / "empty.sql"
    sql_file.write_text(
        "SELECT * FROM customers;",
        encoding="utf-8"
    )

    config = {
        "application": {
            "input_encoding": "utf-8",
            "output_encoding": "utf-8",
            "output_indent": 4
        },
        "logging": {
            "level": "INFO",
            "format": "%(message)s",
            "file": "extraction.log"
        }
    }

    monkeypatch.setattr(
        extraction,
        "load_config",
        lambda: config
    )
    monkeypatch.setattr(
        extraction,
        "setup_logging",
        lambda logging_config: logging.getLogger("test")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["extraction.py", str(sql_file)]
    )

    result = extraction.main()

    output_file = tmp_path / "empty.json"
    output_data = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert result == 0
    assert output_data == {"procedures": []}
