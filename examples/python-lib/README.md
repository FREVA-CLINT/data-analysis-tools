# Using a Tool by Installing a Python Package

This example demonstrates how to define a tool as a Python package that can be
installed via standard Python packaging tools. The package is defined using a
`pyproject.toml`, `setup.cfg`, or `setup.py` file. The recommended approach is
to use `pyproject.toml`, which allows you to merge the `tool.toml` file into a
single configuration.

## Purpose

This configuration allows you to:
1. Define a Python package that can be deployed and installed using standard
   Python packaging tools.
2. Merge the `tool.toml` configuration into the `pyproject.toml` file for a
   streamlined setup.
3. Leverage the `tool.run.command` section to execute an entry-point script
   defined in your Python package.

## How It Works

1. **Package Definition**:
   - The tool is defined as a Python package using `pyproject.toml`,
     `setup.cfg`, or `setup.py`.
   - The `pyproject.toml` file is the recommended format, as it supports
     modern Python packaging standards and allows merging with the
     `tool.toml` file.

2. **Command Configuration**:
   - After the package is installed, the `tool.run.command` section of the
     `pyproject.toml` file should reference the entry-point script defined in
     the package.

3. **Version Management**:
   - When merging `tool.toml` into `pyproject.toml`, the `version` entry
     should only be defined in the `[project]` section of `pyproject.toml`.

4. **Tool Execution**:
   - The installed Python package provides entry points for the tool, allowing
     users to execute commands via the entry-point script.

## Example Use Case

- **Data Analysis Library**:
  Create a Python library for analyzing datasets, where the main tool logic is
  exposed through an entry-point script.

- **Custom CLI Tool**:
  Develop a command-line tool as a Python package, enabling users to install
  it via `pip` and execute commands using a defined entry-point.

## Notes

- Ensure your `pyproject.toml` file adheres to the
  [PEP 621](https://peps.python.org/pep-0621/) standard for defining project
  metadata.
- Clearly document the entry-point script in the `[project.scripts]` section
  of `pyproject.toml`.
- The `tool.run.command` in the merged `pyproject.toml` file should point to
  the entry-point defined in the `[project.scripts]` section.
