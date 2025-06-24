import json
import os
import pytest
from pathlib import Path

from commands.generate_openapi_schema import (
    generate_openapi_schema,
    remove_operation_id_tag,
)


def load_json_file(filename):
    test_dir = os.path.dirname(__file__)
    file_path = os.path.join(test_dir, "files", filename)
    with open(file_path, "r") as f:
        return json.load(f)


@pytest.fixture
def sample_openapi_schema():
    return load_json_file("openapi_test.json")


@pytest.fixture
def expected_output_schema():
    return load_json_file("openapi_test_output.json")


def test_remove_operation_id_tag(sample_openapi_schema, expected_output_schema):
    cleaned_schema = remove_operation_id_tag(sample_openapi_schema)
    assert cleaned_schema == expected_output_schema


@pytest.fixture
def mock_app(mocker):
    app = mocker.patch("commands.generate_openapi_schema.app")
    app.openapi.return_value = {
        "openapi": "3.1.0",
        "info": {"title": "FastAPI", "version": "0.1.0"},
        "paths": {},
    }
    return app


def test_generate_openapi_schema(mocker, mock_app):
    mock_remove_operation_id_tag = mocker.patch(
        "commands.generate_openapi_schema.remove_operation_id_tag"
    )
    mock_remove_operation_id_tag.return_value = {"mocked_schema": True}

    output_file = "openapi_test.json"
    expected_output = json.dumps({"mocked_schema": True}, indent=2)

    generate_openapi_schema(output_file)

    mock_app.openapi.assert_called_once()
    mock_remove_operation_id_tag.assert_called_once_with(mock_app.openapi.return_value)

    output_path = Path(output_file)
    assert output_path.is_file()
    with open(output_file, "r") as f:
        content = f.read()
        assert content == expected_output

    output_path.unlink()
