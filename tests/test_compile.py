#!/usr/bin/python3

from pathlib import Path

import pytest

import solcx
from solcx.exceptions import ContractsNotFound

# these values should work for all compatible solc versions
combined_json_values = (
    "abi",
    "asm",
    "ast",
    "bin",
    "bin-runtime",
    "devdoc",
    "metadata",
    "opcodes",
    "srcmap",
    "srcmap-runtime",
    "userdoc",
)


@pytest.fixture(autouse=True)
def setup(all_versions):
    pass


def _compile_assertions(output, key):
    assert output
    assert key in output
    for value in combined_json_values:
        assert value in output[key]


def test_compile_source(foo_source):
    output = solcx.compile_source(foo_source)
    _compile_assertions(output, "<stdin>:Foo")
    output = solcx.compile_source(foo_source, optimize=True)
    _compile_assertions(output, "<stdin>:Foo")


def test_compile_source_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_source("  ")
    solcx.compile_source("  ", allow_empty=True)


@pytest.mark.parametrize("key", combined_json_values)
def test_compile_source_output_types(foo_source, key):
    output = solcx.compile_source(foo_source, output_values=[key])
    assert key in output["<stdin>:Foo"]


def test_compile_files_string(foo_path):
    output = solcx.compile_files([foo_path.as_posix()])
    _compile_assertions(output, f"{foo_path.as_posix()}:Foo")


def test_compile_files_optimized(foo_path):
    output = solcx.compile_files([foo_path], optimize=True)
    _compile_assertions(output, f"{foo_path.as_posix()}:Foo")


def test_compile_files_path_object(foo_path):
    output = solcx.compile_files([foo_path])
    _compile_assertions(output, f"{foo_path.as_posix()}:Foo")


def test_compile_files_empty():
    with pytest.raises(ContractsNotFound):
        solcx.compile_files([])
    solcx.compile_files([], allow_empty=True)


@pytest.mark.parametrize("key", combined_json_values)
def test_compile_files_output_types(foo_path, key):
    output = solcx.compile_files([foo_path], output_values=[key])
    assert key in output[f"{foo_path.as_posix()}:Foo"]


def test_compile_source_import_remapping(foo_path, bar_source):
    path = Path(foo_path).parent.as_posix()
    output = solcx.compile_source(bar_source, import_remappings={"contracts": path})

    assert set(output) == {f"{foo_path.as_posix()}:Foo", "<stdin>:Bar"}


def test_compile_files_import_remapping(foo_path, bar_path):
    path = Path(bar_path).parent.as_posix()
    output = solcx.compile_files([bar_path], import_remappings={"contracts": path})

    assert set(output) == {f"{bar_path.as_posix()}:Bar", f"{foo_path.as_posix()}:Foo"}
